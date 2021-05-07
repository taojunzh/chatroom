
from flask import Flask, jsonify, render_template,redirect,url_for,request,session, flash, send_from_directory

from flask_login import current_user, login_user, login_required, logout_user, LoginManager
from flask_socketio import SocketIO,join_room,leave_room

import requests
import datetime
from database import registration, verify, get_userinfo, validate_dis, validate_user, add_room_members, save_room, \
    get_rooms_for_user, is_room_member, get_room, get_room_members, is_room_admin, update_room, remove_room_members
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
    rooms = []
    if current_user.is_authenticated:
        rooms = get_rooms_for_user(current_user.username)
        if current_user.display not in Online_Users:
            Online_Users.append(current_user.display)
    return render_template('index.html', rooms=rooms)



@app.route("/logout/")
@login_required
def logout():
    Online_Users.remove(current_user.display)
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


#private room
@app.route('/create-room/', methods=['GET', 'POST'])
@login_required
def create_room():
    message = ''
    if request.method == 'POST':
        room_name = request.form.get('room_name')
        usernames = [username.strip() for username in request.form.get('members').split(',')]

        if len(room_name) and len(usernames):
            room_id = save_room(room_name, current_user.username)
            if current_user.username in usernames:
                usernames.remove(current_user.username)
            add_room_members(room_id, room_name, usernames, current_user.username)
            return redirect(url_for('view_room', room_id=room_id))
        else:
            message = "Failed to create room"
    return render_template('create_room.html', message=message)
    #return render_template('create_room.html')

@app.route('/rooms/<room_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_room(room_id):
    room = get_room(room_id)
    if room and is_room_admin(room_id, current_user.username):
        existing_room_members = [member['_id']['username'] for member in get_room_members(room_id)]
        room_members_str = ",".join(existing_room_members)
        message = ''
        if request.method == 'POST':
            room_name = request.form.get('room_name')
            room['name'] = room_name
            update_room(room_id, room_name)

            new_members = [username.strip() for username in request.form.get('members').split(',')]
            members_to_add = list(set(new_members) - set(existing_room_members))
            members_to_remove = list(set(existing_room_members) - set(new_members))
            if len(members_to_add):
                add_room_members(room_id, room_name, members_to_add, current_user.username)
            if len(members_to_remove):
                remove_room_members(room_id, members_to_remove)
            message = 'Room edited successfully'
            room_members_str = ",".join(new_members)
        return render_template('edit_room.html', room=room, room_members_str=room_members_str, message=message)
    else:
        return "Room not found", 404


@app.route('/rooms/<room_id>/')
@login_required
def view_room(room_id):
    room = get_room(room_id)
    if room and is_room_member(room_id, current_user.username):
        room_members = get_room_members(room_id)
        return render_template('view_room.html', username=current_user.username, room=room, room_members=room_members)
    else:
        return "Room not found", 404


@socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info("{} has sent message to the room {}: {}".format(data['username'],
                                                                    data['room'],
                                                                    data['message']))
    socketio.emit('receive_message', data, room=data['room'])



@socketio.on('join_room')
def handle_join_room_event(data):
    app.logger.info("{} has joined the room {}".format(data['username'], data['room']))
    join_room(data['room'])
    socketio.emit('join_room_announcement', data, room=data['room'])


@socketio.on('leave_room')
def handle_leave_room_event(data):
    app.logger.info("{} has left the room {}".format(data['username'], data['room']))
    leave_room(data['room'])
    socketio.emit('leave_room_announcement', data, room=data['room'])
#private room ends
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

    socketio.run(app, debug=True)

    #socketio.run(app, host="0.0.0.0", port=5000, debug=True) #use this line when using docker

