
from flask import Flask, render_template,redirect,url_for,request

from flask_login import current_user, login_user, login_required, logout_user, LoginManager
from flask_socketio import SocketIO,join_room,leave_room
from flask_pymongo import PyMongo

import requests
import datetime
from database import *
import bcrypt


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['MONGO_URI'] = myclient = "mongodb://mongo:27017/myFirstDatabase"
# app.config['MONGO_URI'] = myclient = "mongodb+srv://ytc:kevin@cluster0.35txz.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
app.config['SECRET_KEY'] = 'secret!'

mongo = PyMongo(app)
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)
Online_Users = {}

@app.route('/')
def index():
    if current_user.is_authenticated:
        # if current_user.display not in Online_Users:
            # Online_Users.append(current_user.display)
        if mongo.db.images.find_one({'username': current_user.display}):
            user_row = mongo.db.images.find_one({'username': current_user.display})
            image_name = user_row['profile_image_name']
            Online_Users[current_user.display] = image_name
        else:
            Online_Users[current_user.display] = ''
    return render_template('index.html')



@app.route("/logout/")
@login_required
def logout():
    # Online_Users.remove(current_user.display)
    del Online_Users[current_user.display]

    # socketio.emit("user logout", Online_Users)
    logout_user()
    return redirect(url_for('index'))


@app.route('/chatroom')
@login_required
def chatroom():
    return render_template('chatroom.html')


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    message =''
    if request.method == 'POST':
        display = request.form.get('display')
        username = request.form.get('username')
        password = request.form.get('password').encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password, salt)
        if validate_dis(display) and validate_user(username):
            registration(display,username,hashed,salt)
            return redirect(url_for('login'))
        else:
            message= "User or displayname existed"
    return render_template('register.html', msg = message)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    message = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password').encode('utf-8')
        user = get_userinfo(username)
        if user and verify(username,password):
            if user.display in Online_Users.keys():
                message = "Already logged in"
            else:
                login_user(user)
                return redirect(url_for('index'))
        else:
            message ="Invalid username or password. Please try again."
    return render_template('login.html',error = message)

@app.route('/setting', methods=['GET', 'POST'])
@login_required
def setting():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        if request.files['file'].filename == '':
            return redirect(request.url)

        if 'file' in request.files:
            profile_image = request.files['file']
            if profile_image and ('.' in profile_image.filename and profile_image.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS):
                if mongo.db.images.find_one({'username': current_user.display}):
                    mongo.save_file(profile_image.filename, profile_image)
                    mongo.db.images.replace_one({'username': current_user.display},
                                                {'username': current_user.display, 'profile_image_name': profile_image.filename})
                else:
                    mongo.save_file(profile_image.filename, profile_image)
                    mongo.db.images.insert_one(
                        {'username': current_user.display, 'profile_image_name': profile_image.filename})
            return redirect(url_for('index'))
    return render_template('setting.html')

@app.route('/files/<filename>')
def file(filename):
    return mongo.send_file(filename)

@socketio.on('connect')
def connect_handler():
    if current_user.is_authenticated:
        user = current_user.display
        result = intializevote()

        socketio.emit('add user',(user,Online_Users,result[0],result[1]))
    else:
        return False

# @socketio.on("disconnect")
# def disconnect():
#     logout_user()

@socketio.on('vote')
def voting(input):
    storevote(input)

    result1 = countvote(1)
    result2 = countvote(2)
    # print(result1,result2)
    socketio.emit('voting bar',(result1,result2),broadcast =True)

@socketio.on("vote result")
def resulthandler(result,total):
    # print(result)
    storevoteresult(result,total)


@socketio.on("message")
def message(data):
    if(data["type"] == "comment"):
        socketio.send({
            'username': data["username"],
            'comment': HTMLescape(data["comment"]),
            "type": data["type"],
            'time': datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        })
    if(data["type"] == "link"):
        embedded = data["link"].replace(
            "https://www.youtube.com/watch?v=", "https://www.youtube.com/embed/")
        if "&ab_channel=" in embedded:
            embedded = embedded.split("&ab_channel=")
            embedded = embedded[0]

        socketio.send({
            'username': data["username"],
            'link': HTMLescape(data["link"]),
            'embedded': HTMLescape(embedded),
            'valid': check_url(data["link"]),
            "type": data["type"],
            'time': datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        })


def HTMLescape(string):
    return string.replace("&", "&amp").replace("<", "&lt").replace(">", "&gt")


def check_url(url):
    try:
        response = requests.head(url)
        return 1 if (200 == response.status_code and "youtube.com" in url)else 0
    except:
        return 0


@login_manager.user_loader
def load_user(user_id):
    return get_userinfo(user_id)


if __name__ == '__main__':

    # socketio.run(app)
    socketio.run(app, host="0.0.0.0", port=5000, debug=True) #use this line when using docker

