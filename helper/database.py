import pymongo
import os
import datetime
import logging
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

# Insert User Data with Extended Metadata Fields
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
        "metadata": True,  # Default to True for metadata
        "metadata_code": "Telegram : @TechifyBots",
        "title": "Encoded by @TechifyBots",
        "author": "@TechifyBots",
        "artist": "@TechifyBots",
        "audio": "By @TechifyBots",
        "subtitle": "By @TechifyBots",
        "video": "Encoded By @TechifyBots",
        "media_type": None,
        "format_template": None,
        "thumbnails": {},
        "temp_quality": None,
        "use_global_thumb": False,
        "global_thumb": None,
        "ban_status": {
            "is_banned": False,
            "ban_duration": 0,
            "banned_on": datetime.date.max.isoformat(),
            "ban_reason": ''
        },
        "metadata_profile": 1,  # Default profile 1
        # Profile 2 fields
        "title_profile_2": "Encoded by @TechifyBots",
        "author_profile_2": "@TechifyBots",
        "artist_profile_2": "@TechifyBots",
        "audio_profile_2": "By @TechifyBots",
        "subtitle_profile_2": "By @TechifyBots",
        "video_profile_2": "Encoded By @TechifyBots"
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

# ============= Metadata Function Code =============== #
def setmeta(chat_id, bool_meta):
    dbcol.update_one({"_id": chat_id}, {"$set": {"metadata": bool_meta}})

def setmetacode(chat_id, metadata_code):
    dbcol.update_one({"_id": chat_id}, {"$set": {"metadata_code": metadata_code}})

# Extended metadata functions
def get_metadata(user_id):
    user = dbcol.find_one({'_id': int(user_id)})
    return user.get('metadata', True) if user else True

def set_metadata(user_id, metadata):
    dbcol.update_one({'_id': int(user_id)}, {'$set': {'metadata': metadata}})

def get_title(user_id):
    user = dbcol.find_one({'_id': int(user_id)})
    return user.get('title', 'Encoded by @TechifyBots') if user else 'Encoded by @TechifyBots'

def set_title(user_id, title):
    dbcol.update_one({'_id': int(user_id)}, {'$set': {'title': title}})

def get_author(user_id):
    user = dbcol.find_one({'_id': int(user_id)})
    return user.get('author', '@TechifyBots') if user else '@TechifyBots'

def set_author(user_id, author):
    dbcol.update_one({'_id': int(user_id)}, {'$set': {'author': author}})

def get_artist(user_id):
    user = dbcol.find_one({'_id': int(user_id)})
    return user.get('artist', '@TechifyBots') if user else '@TechifyBots'

def set_artist(user_id, artist):
    dbcol.update_one({'_id': int(user_id)}, {'$set': {'artist': artist}})

def get_audio(user_id):
    user = dbcol.find_one({'_id': int(user_id)})
    return user.get('audio', 'By @TechifyBots') if user else 'By @TechifyBots'

def set_audio(user_id, audio):
    dbcol.update_one({'_id': int(user_id)}, {'$set': {'audio': audio}})

def get_subtitle(user_id):
    user = dbcol.find_one({'_id': int(user_id)})
    return user.get('subtitle', "By @TechifyBots") if user else "By @TechifyBots"

def set_subtitle(user_id, subtitle):
    dbcol.update_one({'_id': int(user_id)}, {'$set': {'subtitle': subtitle}})

def get_video(user_id):
    user = dbcol.find_one({'_id': int(user_id)})
    return user.get('video', 'Encoded By @TechifyBots') if user else 'Encoded By @TechifyBots'

def set_video(user_id, video):
    dbcol.update_one({'_id': int(user_id)}, {'$set': {'video': video}})

# Profile Support Functions
def get_current_profile(user_id):
    user = dbcol.find_one({'_id': int(user_id)})
    return user.get('metadata_profile', 1) if user else 1

def set_current_profile(user_id, profile_num):
    dbcol.update_one({'_id': int(user_id)}, {'$set': {'metadata_profile': profile_num}})

def get_metadata_field_with_profile(user_id, field, profile_num=None):
    if profile_num is None:
        profile_num = get_current_profile(user_id)
    
    profile_fields = {
        "title": f"title_profile_{profile_num}" if profile_num == 2 else "title",
        "author": f"author_profile_{profile_num}" if profile_num == 2 else "author",
        "artist": f"artist_profile_{profile_num}" if profile_num == 2 else "artist",
        "audio": f"audio_profile_{profile_num}" if profile_num == 2 else "audio",
        "subtitle": f"subtitle_profile_{profile_num}" if profile_num == 2 else "subtitle",
        "video": f"video_profile_{profile_num}" if profile_num == 2 else "video"
    }
    
    field_key = profile_fields.get(field)
    if not field_key:
        return None
    
    user = dbcol.find_one({"_id": int(user_id)})
    if user and field_key in user:
        return user.get(field_key)
    else:
        # Fallback to default method
        method_name = f"get_{field}"
        method = globals().get(method_name)
        if method:
            return method(user_id)
    return None

def set_metadata_field_with_profile(user_id, field, value, profile_num=None):
    if profile_num is None:
        profile_num = get_current_profile(user_id)
    
    profile_fields = {
        "title": f"title_profile_{profile_num}" if profile_num == 2 else "title",
        "author": f"author_profile_{profile_num}" if profile_num == 2 else "author",
        "artist": f"artist_profile_{profile_num}" if profile_num == 2 else "artist",
        "audio": f"audio_profile_{profile_num}" if profile_num == 2 else "audio",
        "subtitle": f"subtitle_profile_{profile_num}" if profile_num == 2 else "subtitle",
        "video": f"video_profile_{profile_num}" if profile_num == 2 else "video"
    }
    
    field_key = profile_fields.get(field)
    if not field_key:
        return False
    
    dbcol.update_one({"_id": int(user_id)}, {"$set": {field_key: value}})
    return True

def get_all_profiles_summary(user_id):
    summary = {}
    
    for profile_num in [1, 2]:
        profile_data = {}
        for field in ["title", "author", "artist", "audio", "subtitle", "video"]:
            value = get_metadata_field_with_profile(user_id, field, profile_num)
            profile_data[field] = value
        summary[f"profile_{profile_num}"] = profile_data
    
    return summary

def copy_profile_to_profile(user_id, from_profile, to_profile):
    fields = ["title", "author", "artist", "audio", "subtitle", "video"]
    
    for field in fields:
        # Get value from source profile
        from_field = f"{field}_profile_{from_profile}" if from_profile == 2 else field
        user = dbcol.find_one({"_id": int(user_id)})
        value = user.get(from_field) if user else None
        
        if value is None:
            # If source profile field doesn't exist, get default
            method_name = f"get_{field}"
            method = globals().get(method_name)
            if method:
                value = method(user_id)
        
        # Set to target profile
        to_field = f"{field}_profile_{to_profile}" if to_profile == 2 else field
        dbcol.update_one({"_id": int(user_id)}, {"$set": {to_field: value}})
    return True

# ============= Metadata Function Code =============== #

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
            metadata = False
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
