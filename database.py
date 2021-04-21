from User import User
import pymongo
myclient = pymongo.MongoClient("mongodb+srv://ytc:kevin@cluster0.35txz.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = myclient.user_login_system
import bcrypt

def register(display,username,password,salt):
    db.insertOne({'dis_name':display,'user':username,'pass':password,'pass_salt':salt})

def get_userinfo(username):
    userinfo = db.findOne({'user': username})
    if userinfo:
        return User(userinfo['dis_name'],userinfo['user'],userinfo['pass'])

def verify(username,password):
    userinfo = db.findOne({'user': username})
    salt =userinfo['pass_salt']
    hash = userinfo['pass']
    if bcrypt.hashpw(password.encode('utf-8'),salt) == hash:
        return True
    else :
        return False