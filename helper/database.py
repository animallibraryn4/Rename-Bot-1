import pymongo
import os
import datetime
from helper.date import add_date
from config import *

mongo = pymongo.MongoClient(DATABASE_URL)
db = mongo[DATABASE_NAME]
dbcol = db["user"]

# Total User
def total_user():
    user = dbcol.count_documents({})
    return user

# Insert Bot Data
def botdata(chat_id):
    bot_id = int(chat_id)
    try:
        bot_data = {"_id": bot_id, "total_rename": 0, "total_size": 0}
        dbcol.insert_one(bot_data)
    except:
        pass

# Total Renamed Files
def total_rename(chat_id, renamed_file):
    now = int(renamed_file) + 1
    dbcol.update_one({"_id": chat_id}, {"$set": {"total_rename": str(now)}})

# Total Renamed File Size
def total_size(chat_id, total_size, now_file_size):
    now = int(total_size) + now_file_size
    dbcol.update_one({"_id": chat_id}, {"$set": {"total_size": str(now)}})

# Insert User Data with Advanced Metadata Fields
def insert(chat_id):
    user_id = int(chat_id)
    user_det = {
        "_id": user_id, 
        "file_id": None, 
        "caption": None, 
        "daily": 0, 
        "date": 0,
        "uploadlimit": 5368709120, 
        "used_limit": 0, 
        "usertype": "Free", 
        "prexdate": None,
        "metadata": "Off",  # Changed from Boolean to String "On"/"Off"
        "metadata_code": "By @TechifyBots",
        # Advanced metadata fields
        "title": "Encoded by @TechifyBots",
        "author": "@TechifyBots",
        "artist": "@TechifyBots",
        "audio": "By @TechifyBots",
        "subtitle": "By @TechifyBots",
        "video": "Encoded By @TechifyBots",
        "editing_metadata_field": "",  # For editing state
        "editing_message_id": ""       # For editing state
    }
    try:
        dbcol.insert_one(user_det)
    except:
        return True

# Add Thumbnail Data
def addthumb(chat_id, file_id):
    dbcol.update_one({"_id": chat_id}, {"$set": {"file_id": file_id}})

def delthumb(chat_id):
    dbcol.update_one({"_id": chat_id}, {"$set": {"file_id": None}})

# ============= ADVANCED METADATA FUNCTIONS =============== #

def setmeta(chat_id, bool_meta):
    """Set metadata status - 'On' or 'Off'"""
    dbcol.update_one({"_id": chat_id}, {"$set": {"metadata": bool_meta}})

def setmetacode(chat_id, metadata_code):
    """Set custom metadata code (legacy)"""
    dbcol.update_one({"_id": chat_id}, {"$set": {"metadata_code": metadata_code}})

# Title functions
def set_title(chat_id, title):
    dbcol.update_one({"_id": chat_id}, {"$set": {"title": title}})

def get_title(chat_id):
    user = dbcol.find_one({"_id": chat_id})
    return user.get("title", "Encoded by @TechifyBots") if user else "Encoded by @TechifyBots"

# Author functions
def set_author(chat_id, author):
    dbcol.update_one({"_id": chat_id}, {"$set": {"author": author}})

def get_author(chat_id):
    user = dbcol.find_one({"_id": chat_id})
    return user.get("author", "@TechifyBots") if user else "@TechifyBots"

# Artist functions
def set_artist(chat_id, artist):
    dbcol.update_one({"_id": chat_id}, {"$set": {"artist": artist}})

def get_artist(chat_id):
    user = dbcol.find_one({"_id": chat_id})
    return user.get("artist", "@TechifyBots") if user else "@TechifyBots"

# Audio functions
def set_audio(chat_id, audio):
    dbcol.update_one({"_id": chat_id}, {"$set": {"audio": audio}})

def get_audio(chat_id):
    user = dbcol.find_one({"_id": chat_id})
    return user.get("audio", "By @TechifyBots") if user else "By @TechifyBots"

# Subtitle functions
def set_subtitle(chat_id, subtitle):
    dbcol.update_one({"_id": chat_id}, {"$set": {"subtitle": subtitle}})

def get_subtitle(chat_id):
    user = dbcol.find_one({"_id": chat_id})
    return user.get("subtitle", "By @TechifyBots") if user else "By @TechifyBots"

# Video functions
def set_video(chat_id, video):
    dbcol.update_one({"_id": chat_id}, {"$set": {"video": video}})

def get_video(chat_id):
    user = dbcol.find_one({"_id": chat_id})
    return user.get("video", "Encoded By @TechifyBots") if user else "Encoded By @TechifyBots"

# Editing state functions
def set_editing_state(chat_id, field, message_id):
    dbcol.update_one({"_id": chat_id}, {"$set": {
        "editing_metadata_field": field,
        "editing_message_id": message_id
    }})

def clear_editing_state(chat_id):
    dbcol.update_one({"_id": chat_id}, {"$unset": {
        "editing_metadata_field": "",
        "editing_message_id": ""
    }})

def get_editing_state(chat_id):
    user = dbcol.find_one({"_id": chat_id})
    if user:
        field = user.get("editing_metadata_field", "")
        message_id = user.get("editing_message_id", "")
        return field, message_id
    return "", ""

# ============= METADATA FUNCTION CODE =============== #

# Add Caption Data
def addcaption(chat_id, caption):
    dbcol.update_one({"_id": chat_id}, {"$set": {"caption": caption}})

def delcaption(chat_id):
    dbcol.update_one({"_id": chat_id}, {"$set": {"caption": None}})

def dateupdate(chat_id, date):
    dbcol.update_one({"_id": chat_id}, {"$set": {"date": date}})

def used_limit(chat_id, used):
    dbcol.update_one({"_id": chat_id}, {"$set": {"used_limit": used}})

def usertype(chat_id, type):
    dbcol.update_one({"_id": chat_id}, {"$set": {"usertype": type}})

def uploadlimit(chat_id, limit):
    dbcol.update_one({"_id": chat_id}, {"$set": {"uploadlimit": limit}})

# Add Premium Data
def addpre(chat_id):
    date = add_date()
    dbcol.update_one({"_id": chat_id}, {"$set": {"prexdate": date[0]}})

def addpredata(chat_id):
    dbcol.update_one({"_id": chat_id}, {"$set": {"prexdate": None}})

def daily(chat_id, date):
    dbcol.update_one({"_id": chat_id}, {"$set": {"daily": date}})

def find(chat_id):
    id = {"_id": chat_id}
    x = dbcol.find(id)
    for i in x:
        file = i.get("file_id", None)
        caption = i.get("caption", None)
        metadata = i.get("metadata", "Off")
        metadata_code = i.get("metadata_code", "By @TechifyBots")
        title = i.get("title", "Encoded by @TechifyBots")
        author = i.get("author", "@TechifyBots")
        artist = i.get("artist", "@TechifyBots")
        audio = i.get("audio", "By @TechifyBots")
        subtitle = i.get("subtitle", "By @TechifyBots")
        video = i.get("video", "Encoded By @TechifyBots")
        
        return [file, caption, metadata, metadata_code, title, author, artist, audio, subtitle, video]

def getid():
    values = []
    for key in dbcol.find():
        id = key["_id"]
        values.append((id))
    return values

def delete(id):
    dbcol.delete_one(id)

def find_one(id):
    return dbcol.find_one({"_id": id})
