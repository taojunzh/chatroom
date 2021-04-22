from User import User
import pymongo
myclient = pymongo.MongoClient("mongodb://mongo:27017")  #for docker

db = myclient.user_login_system
import bcrypt

def registration(display,username,password,salt):
    user = {'dis_name':display,'_id':username,'pass':password,'pass_salt':salt}
    db.users.insert_one(user)

def get_userinfo(username):
    userinfo = db.users.find_one({'_id': username})
    if userinfo:
        return User(userinfo['dis_name'],userinfo['_id'],userinfo['pass'])

def verify(username,password):
    userinfo = db.users.find_one({'_id': username})
    salt =userinfo['pass_salt']
    hash = userinfo['pass']
    if bcrypt.hashpw(password,salt) == hash:
        return True
    else :
        return False

def validate_dis(display):
    if db.users.find_one({'dis_name': display}):
        return False
    else:
        return True

def validate_user(username):
    if db.users.find_one({'username': username}):
        return False
    else:
        return True
