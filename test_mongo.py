from flask import Flask, jsonify, render_template,redirect,url_for,request,session

from flask_login import current_user, login_user, login_required, logout_user, LoginManager
from flask_socketio import SocketIO
import requests
import datetime
from User import User
from database import register,verify,get_userinfo
import bcrypt
from pymongo.errors import DuplicateKeyError

#from passlib.hash import pbkdf2_sha256
#chat_history_database.drop()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)
Online_Users=[]



def start_session(self, user):
        del user['password']
        session['logged_in'] = True
        session['user'] = user
        Online_Users.append(user["display"].title())
        # Online_Users.append("d2")
        return


@app.route('/')
def index():
    return render_template('index.html')

@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/chatroom')
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
        try:
            register(display,username,hashed,salt)
            return redirect(url_for('login'))
        except DuplicateKeyError:
            message= "User existed"
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
            return redirect(url_for('index'))
        else:
            message ="Invalid username or password. Please try again."
    return render_template('login.html',error = message)

# @app.route("/chatroom", methods=["GET", "POST"])
# def chatroom():
#     return render_template('chatroom.html')

@socketio.on('connection established')
def connect():
    print("connection established")
    new_onlineuser =session.get('user')
    new_onlineuser = new_onlineuser['display']
    print(session)
    print(Online_Users)
    socketio.emit('connection received',(new_onlineuser,Online_Users))

# @socketio.on('disconnect')
# def disconnect():
#     dis_user= session.get('user')
#     Online_Users.remove(dis_user['display'])
#
#     socketio.emit('disconnectd',dis_user['display'])
@socketio.on("message")
def message(data):
    if(data["type"]=="comment"):
        socketio.send({
        'username': data["username"],
        'comment': HTMLescape(data["comment"]),
        "type": data["type"],
        'time': datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        })
    if(data["type"]=="link"):
        embedded= data["link"].replace("https://www.youtube.com/watch?v=","https://www.youtube.com/embed/")
        if "&ab_channel=" in embedded:
            embedded= embedded.split("&ab_channel=")
            embedded= embedded[0]

        socketio.send({
        'username': data["username"],
        'link': HTMLescape(data["link"]),
        'embedded': HTMLescape(embedded),
        'valid': check_url(data["link"]),
        "type": data["type"],
        'time': datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        })

def HTMLescape(string):
    return string.replace("&","&amp").replace("<","&lt").replace(">","&gt")

def check_url(url):
    try:
        response = requests.head(url)
        return 1 if (200==response.status_code and "youtube.com" in url )else 0
    except:
        return 0

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

if __name__ == '__main__':

    #socketio.run(app)
    # socketio.run(app, host="0.0.0.0", port=5000, debug=True) #use this line when using docker
    app.run(port=5000, debug=True)
