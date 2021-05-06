from User import User
import pymongo
# myclient = pymongo.MongoClient("mongodb://mongo:27017")  #for docker
myclient = pymongo.MongoClient("mongodb+srv://ytc:kevin@cluster0.35txz.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = myclient.user_login_system
votedb = myclient.vote
onlinedb = myclient.online

import bcrypt

def intializevote():
    result= votedb.result.find_one({'_id':1})
    if not result:
        votedb.result.insert_one({'_id':1,'result':0})
        return 0
    else:
        return result['result']
        # get_voteresult()


def storevote(vote):
    voting = {'vote' + str(vote): 1}
    votedb.voting.insert_one(voting)

def countvote(vote):
    count = 0
    if votedb.voting.find({'vote' +str(vote): 1}):
        count = votedb.voting.find({'vote' +str(vote): 1}).count()
    return count

def storevoteresult(result):
    print(result)
    db = votedb.result.replace_one({"_id" :1},
                            {"_id":1, 'result':result}
                              )
    print(db)

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
