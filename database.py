from User import User
import pymongo
myclient = pymongo.MongoClient("mongodb://mongo:27017")  #for docker
# myclient = pymongo.MongoClient("mongouserdb+srv://ytc:kevin@cluster0.35txz.mongouserdb.net/myFirstDatabase?retryWrites=true&w=majority")
userdb = myclient.user_login_system
voteuserdb = myclient.vote
onlineuserdb = myclient.online

import bcrypt

def intializevote():
    result= voteuserdb.result.find_one({'_id':1})
    if not result:
        voteuserdb.result.insert_one({'_id':1,'result':0,'total':0})
        return 0
    else:
        return (result['result'],result['total'])
        # get_voteresult()


def storevote(vote):
    voting = {'vote' + str(vote): 1}
    voteuserdb.voting.insert_one(voting)

def countvote(vote):
    count = 0
    if voteuserdb.voting.find({'vote' +str(vote): 1}):
        count = voteuserdb.voting.find({'vote' +str(vote): 1}).count()
    return count

def storevoteresult(result,total):
    userdb = voteuserdb.result.replace_one({"_id" :1},
                            {"_id":1, 'result':result,'total':total}
                              )

def registration(display,username,password,salt):
    user = {'dis_name':display,'_id':username,'pass':password,'pass_salt':salt}
    userdb.users.insert_one(user)

def get_userinfo(username):
    userinfo = userdb.users.find_one({'_id': username})
    if userinfo:
        return User(userinfo['dis_name'],userinfo['_id'],userinfo['pass'])

def verify(username,password):
    userinfo = userdb.users.find_one({'_id': username})
    salt =userinfo['pass_salt']
    hash = userinfo['pass']
    if bcrypt.hashpw(password,salt) == hash:
        return True
    else :
        return False

def validate_dis(display):
    if userdb.users.find_one({'dis_name': display}):
        return False
    else:
        return True

def validate_user(username):
    if userdb.users.find_one({'username': username}):
        return False
    else:
        return True
