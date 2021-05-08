from User import User
from datetime import datetime
from bson import ObjectId
import pymongo
# myclient = pymongo.MongoClient("mongodb://mongo:27017")  #for docker
myclient = pymongo.MongoClient("mongodb+srv://ytc:kevin@cluster0.35txz.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = myclient.user_login_system
votedb = myclient.vote
onlinedb = myclient.online

import bcrypt

private_room_db = myclient.get_database("private_room_db")
db_rooms = private_room_db.get_collection("rooms")
room_members = private_room_db.get_collection("room_members")

def add_room(room_name, owner):
    room_id = db_rooms.insert_one(
        {'name': room_name, 'owner': owner}).inserted_id
    room_members.insert_one(
        {'_id': {'room_id': ObjectId(room_id), 'username': owner}, 'room_name': room_name, 'added_by': owner})
    return room_id

def delete_room(room_id):
    #db_rooms.remove({'_id': ObjectId(room_id)})
    room_members.remove( {'_id': ObjectId(room_id)})

def get_room(room_id):
    return db_rooms.find_one({'_id': ObjectId(room_id)})

def add_room_members(room_id, room_name, usernames, added_by):
    room_members.insert_many(
        [{'_id': {'room_id': ObjectId(room_id), 'username': username}, 'room_name': room_name, 'added_by': added_by} for username in usernames])

def get_room_members(room_id):
    return list(room_members.find({'_id.room_id': ObjectId(room_id)}))

def get_rooms_for_user(username):
    return list(room_members.find({'_id.username': username}))

def is_room_member(room_id, username):
    return room_members.count_documents({'_id': {'room_id': ObjectId(room_id), 'username': username}})


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
    db = votedb.result.replace_one({"_id" :1},
                            {"_id":1, 'result':result}
                              )

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
