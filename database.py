from User import User
import pymongo
myclient = pymongo.MongoClient("mongodb+srv://ytc:kevin@cluster0.35txz.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
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
    if bcrypt.hashpw(password   ,salt) == hash:
        return True
    else :
        return False