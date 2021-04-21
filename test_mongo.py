
from flask import Flask, jsonify, render_template,redirect,url_for,request,session, flash, send_from_directory

from flask_login import current_user, login_user, login_required, logout_user, LoginManager
from flask_socketio import SocketIO,join_room,leave_room

import requests
import datetime
from database import registration,verify,get_userinfo,validate_dis,validate_user
import bcrypt
import os
from pymongo.errors import DuplicateKeyError

#from passlib.hash import pbkdf2_sha256
#chat_history_database.drop()
FolderPath = 'C:\\Users\\Liang\\Desktop\\cse312Project\\chatroom\\static\\Files'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = FolderPath
app.config['SECRET_KEY'] = 'secret!'

socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)
Online_Users = []




@app.route('/')
def index():
        return render_template('index.html')


@app.route("/logout/")
@login_required
def logout():
    Online_Users.remove(current_user.display)
    logout_user()
    return redirect(url_for('index'))


@app.route('/chatroom')
def chatroom():
    if len(Online_Users) > 0:
        return render_template('chatroom.html')
    else:
        return redirect(url_for('index'))


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
            login_user(user)
            Online_Users.append(current_user.display)
            return redirect(url_for('index'))
        else:
            message ="Invalid username or password. Please try again."
    return render_template('login.html',error = message)

# @app.route("/chatroom", methods=["GET", "POST"])
# def chatroom():
#     return render_template('chatroom.html')

@app.route('/setting', methods = ['GET', 'POST'])
def setting():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS): #check for picture extensions
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            return redirect(url_for('uploaded_file', filename=file.filename))
    return render_template('setting.html')

@app.route('/chatroom/static/Files/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@socketio.on('connect')
def connect_handler():
    if current_user.is_authenticated:
        user = current_user.display
        print(Online_Users)
        socketio.emit('add user',(user,Online_Users))
    else:
        return False

@socketio.on("disconnect")
def disconnect():
    logout_user()

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

