from flask import Flask, jsonify, render_template,redirect,url_for,request,session
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

import uuid
import pymongo
#from passlib.hash import pbkdf2_sha256
myclient = pymongo.MongoClient('mongo')
db = myclient.user_login_system
#chat_history_database.drop()
accounts_collection = db["accounts"]


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
mydb= SQLAlchemy(app)
Online_Users=[]


class User:

    def start_session(self, user):
        del user['password']
        session['logged_in'] = True
        session['user'] = user
        #Online_Users.append(user["display"].title())
        Online_Users.append("d2")
        print(user["display"].title())
        return

    def signup(self):
        print(request.form)
        user = {
            "_id": uuid.uuid4().hex,
            "display": request.form.get('display'),
            "user": request.form.get('username'),
            "password": request.form.get('password')
        }

        # Encrypt the password
        #user['password'] = pbkdf2_sha256.encrypt(user['password'])
        if db.users.insert_one(user):
            self.start_session(user)
            #return redirect(url_for('login'))
        else:
            return render_template('register.html', error="register failed.")


    def login(self):

        user = db.users.find_one({
            "user": request.form.get('username')
        })

        #if user and pbkdf2_sha256.verify(request.form.get('password'), user['password']):
        if user and request.form.get('password') == user['password']:
            self.start_session(user)
            return redirect(url_for('chatroom'))

        return render_template('login.html', error="Invalid username or password. Please try again.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chatroom')
def chatroom():
    return render_template('chatroom.html')

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
    new_onlineuser =session.get('display')
    print(new_onlineuser)
    socketio.emit('connection received',(new_onlineuser))

if __name__ == '__main__':

    #socketio.run(app)
    socketio.run(app, host="0.0.0.0", port=5000, debug=True) #use this line when using docker
    #app.run(port=5000, debug=True)