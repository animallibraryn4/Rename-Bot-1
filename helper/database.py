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

# Insert User Data - UPDATED WITH ALL METADATA FIELDS
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
        "metadata": "Off",  # Changed from boolean to string "On"/"Off"
        "metadata_code": "By @TechifyBots",  # Keeping old field for backward compatibility
        # New metadata fields
        "title": "Encoded by @TechifyBots",
        "author": "@TechifyBots",
        "artist": "@TechifyBots",
        "audio": "By @TechifyBots",
        "subtitle": "By @TechifyBots",
        "video": "Encoded By @TechifyBots"
    }
    try:
        dbcol.insert_one(user_det)
    except:
        return True
        pass

# Add Thumbnail Data
def addthumb(chat_id, file_id):
    dbcol.update_one({"_id": chat_id}, {"$set": {"file_id": file_id}})

def delthumb(chat_id):
    dbcol.update_one({"_id": chat_id}, {"$set": {"file_id": None}})

# ============= NEW METADATA FUNCTIONS =============== #
def setmeta(chat_id, metadata_status):
    """Set metadata status: "On" or "Off" """
    dbcol.update_one({"_id": chat_id}, {"$set": {"metadata": metadata_status}})

def get_metadata(chat_id):
    """Get metadata status"""
    user = dbcol.find_one({"_id": chat_id})
    return user.get("metadata", "Off") if user else "Off"

def get_title(chat_id):
    """Get title metadata"""
    user = dbcol.find_one({"_id": chat_id})
    return user.get("title", "Encoded by @TechifyBots") if user else "Encoded by @TechifyBots"

def set_title(chat_id, title):
    """Set title metadata"""
    dbcol.update_one({"_id": chat_id}, {"$set": {"title": title}})

def get_author(chat_id):
    """Get author metadata"""
    user = dbcol.find_one({"_id": chat_id})
    return user.get("author", "@TechifyBots") if user else "@TechifyBots"

def set_author(chat_id, author):
    """Set author metadata"""
    dbcol.update_one({"_id": chat_id}, {"$set": {"author": author}})

def get_artist(chat_id):
    """Get artist metadata"""
    user = dbcol.find_one({"_id": chat_id})
    return user.get("artist", "@TechifyBots") if user else "@TechifyBots"

def set_artist(chat_id, artist):
    """Set artist metadata"""
    dbcol.update_one({"_id": chat_id}, {"$set": {"artist": artist}})

def get_audio(chat_id):
    """Get audio metadata"""
    user = dbcol.find_one({"_id": chat_id})
    return user.get("audio", "By @TechifyBots") if user else "By @TechifyBots"

def set_audio(chat_id, audio):
    """Set audio metadata"""
    dbcol.update_one({"_id": chat_id}, {"$set": {"audio": audio}})

def get_subtitle(chat_id):
    """Get subtitle metadata"""
    user = dbcol.find_one({"_id": chat_id})
    return user.get("subtitle", "By @TechifyBots") if user else "By @TechifyBots"

def set_subtitle(chat_id, subtitle):
    """Set subtitle metadata"""
    dbcol.update_one({"_id": chat_id}, {"$set": {"subtitle": subtitle}})

def get_video(chat_id):
    """Get video metadata"""
    user = dbcol.find_one({"_id": chat_id})
    return user.get("video", "Encoded By @TechifyBots") if user else "Encoded By @TechifyBots"

def set_video(chat_id, video):
    """Set video metadata"""
    dbcol.update_one({"_id": chat_id}, {"$set": {"video": video}})

# Old function for backward compatibility
def setmetacode(chat_id, metadata_code):
    dbcol.update_one({"_id": chat_id}, {"$set": {"metadata_code": metadata_code}})

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
        file = i["file_id"]
        try:
            caption = i["caption"]
        except:
            caption = None
        try:
            metadata = i["metadata"]
        except:
            metadata = "Off"
        try:
            metadata_code = i["metadata_code"]
        except:
            metadata_code = None
            
        return [file, caption, metadata, metadata_code]

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
