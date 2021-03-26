from flask import Flask, render_template,redirect,url_for,request,session
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db= SQLAlchemy(app)
Online_Users=[]

class Login(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username= db.Column(db.String(200),nullable=False)
    password = db.Column(db.String(200), nullable=False)
    displayname = db.Column(db.String(200), nullable=False)
    def __init__(self, username,password,displayname):
        self.username = username
        self.password = password
        self.displayname =displayname
    def __repr__(self):
        return '<User %r>' % self.username

db.create_all()
db.session.commit()
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chatroom')
def chatroom():
    return render_template('chatroom.html')

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        display = request.form.get('display')
        user = request.form.get('username')
        password = request.form.get('password')
        new_user = Login(username= user,displayname=display,password=password)
        db.session.add(new_user)
        db.session.commit()
        Createsession(new_user)
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        password = request.form.get('password')
        user = Login.query.filter_by(username = user).first()
        if user is None or user.password != password:
            return render_template('login.html', error="Invalid username or password. Please try again.")
        else:
            Createsession(user)
            return redirect(url_for('index'))
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

def Createsession(newuser):
    session['display']= newuser.displayname.title()
    session['username'] = newuser.username
    session['userID'] = newuser.id
    Online_Users.append(newuser.displayname.title())

if __name__ == '__main__':
    socketio.run(app)