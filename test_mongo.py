from flask import Flask, jsonify, render_template, redirect, url_for, request, session
from flask_socketio import SocketIO, join_room, leave_room
from flask_login import current_user, login_user, login_required, logout_user, LoginManager
from flask_sqlalchemy import SQLAlchemy

import requests
import datetime
import uuid
import pymongo
import bcrypt
#from passlib.hash import pbkdf2_sha256
myclient = pymongo.MongoClient("mongodb://mongo:27017")
db = myclient.user_login_system
# chat_history_database.drop()

accounts_collection = db["accounts"]


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
# app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///test.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)
Online_Users = []


class User:

    # def __init__(self,display,username,password):
    #     self.username =username
    #     self.display = display
    #     self.password = password
    #
    # @staticmethod
    # def is_authenticated():
    #     return True
    #
    # @staticmethod
    # def is_active():
    #     return True

    def start_session(self, user):
        del user['password']
        session['logged_in'] = True
        session['user'] = user
        Online_Users.append(user["display"].title())
        # Online_Users.append("d2")
        return

    def signup(self):
        # print(request.form)
        password = request.form.get('password').encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password, salt)
        user = {
            "_id": uuid.uuid4().hex,
            "display": request.form.get('display'),
            "user": request.form.get('username'),
            "password": hashed,
            "password_salt": salt
        }
        # user = {
        #     "_id": uuid.uuid4().hex,
        #     "display": request.form.get('display'),
        #     "user": request.form.get('username'),
        #     "password": request.form.get('password')
        # }

        # Encrypt the password
        #user['password'] = pbkdf2_sha256.encrypt(user['password'])
        if db.users.insert_one(user):
            self.start_session(user)
            return redirect(url_for('login'))
        else:
            return render_template('register.html', error="register failed.")


    def login(self):

        user = db.users.find_one({
            "user": request.form.get('username')
        })
        password = request.form.get('password').encode("utf-8")

        salt = user["password_salt"]
        hashed = bcrypt.hashpw(password, salt)
        # if user and pbkdf2_sha256.verify(request.form.get('password'), user['password']):
        if user and hashed == user['password']:
            self.start_session(user)
            return redirect(url_for('index'))

        return render_template('login.html', error="Invalid username or password. Please try again.")


@app.route('/')
def index():
    print(session.get("user")['display'])
    if session.get("user")['display']:
        return render_template('index.html', status="you have logged in")
    else:
        return render_template('index.html', status="Please Login first")


@app.route("/logout/")
@login_required
def logout():
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
    if request.method == 'POST':
        return User().signup()
    return render_template('register.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        return User().login()

    return render_template('login.html')

# @app.route("/chatroom", methods=["GET", "POST"])
# def chatroom():
#     return render_template('chatroom.html')


@socketio.on('connection established')
def connect():
    print("connection established")
    new_onlineuser = session.get('user')
    new_onlineuser = new_onlineuser['display']

    socketio.emit('connection received', (new_onlineuser, Online_Users))

# @socketio.on('disconnect')
# def disconnect():
#     dis_user= session.get('user')
#     Online_Users.remove(dis_user['display'])
#
#     socketio.emit('disconnectd',dis_user['display'])
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
    return User.get(user_id)


if __name__ == '__main__':

    # socketio.run(app)
    # use this line when using docker
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
    # app.run(port=5000, debug=True)
