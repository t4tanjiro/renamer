import pymongo
from helper.date import add_date
from config import *

mongo = pymongo.MongoClient(DB_URL)
db = mongo[DB_NAME]
dbcol = db["user"]


# =========================
# 👥 TOTAL USERS
# =========================
def total_user():
    return dbcol.count_documents({})


# =========================
# 🤖 BOT DATA
# =========================
def botdata(chat_id):
    try:
        dbcol.insert_one({
            "_id": int(chat_id),
            "total_rename": 0,
            "total_size": 0
        })
    except:
        pass


def total_rename(chat_id, renamed_file):
    now = int(renamed_file) + 1
    dbcol.update_one({"_id": chat_id}, {"$set": {"total_rename": str(now)}})


def total_size(chat_id, total_size, now_file_size):
    now = int(total_size) + now_file_size
    dbcol.update_one({"_id": chat_id}, {"$set": {"total_size": str(now)}})


# =========================
# 👤 USER INSERT
# =========================
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

        # 🔥 REFERRAL FIELDS
        "referrals": 0,
        "points": 0,
        "referred_by": None
    }

    try:
        dbcol.insert_one(user_det)
    except:
        pass


# =========================
# 🖼 THUMBNAIL
# =========================
def addthumb(chat_id, file_id):
    dbcol.update_one({"_id": chat_id}, {"$set": {"file_id": file_id}})


def delthumb(chat_id):
    dbcol.update_one({"_id": chat_id}, {"$set": {"file_id": None}})


# =========================
# 📝 CAPTION
# =========================
def addcaption(chat_id, caption):
    dbcol.update_one({"_id": chat_id}, {"$set": {"caption": caption}})


def delcaption(chat_id):
    dbcol.update_one({"_id": chat_id}, {"$set": {"caption": None}})


# =========================
# 📅 DATE / LIMIT
# =========================
def dateupdate(chat_id, date):
    dbcol.update_one({"_id": chat_id}, {"$set": {"date": date}})


def used_limit(chat_id, used):
    dbcol.update_one({"_id": chat_id}, {"$set": {"used_limit": used}})


def usertype(chat_id, type):
    dbcol.update_one({"_id": chat_id}, {"$set": {"usertype": type}})


def uploadlimit(chat_id, limit):
    dbcol.update_one({"_id": chat_id}, {"$set": {"uploadlimit": limit}})


def addpre(chat_id):
    date = add_date()
    dbcol.update_one({"_id": chat_id}, {"$set": {"prexdate": date[0]}})


def addpredata(chat_id):
    dbcol.update_one({"_id": chat_id}, {"$set": {"prexdate": None}})


def daily(chat_id, date):
    dbcol.update_one({"_id": chat_id}, {"$set": {"daily": date}})


# =========================
# 🔍 FIND
# =========================
def find(chat_id):
    data = dbcol.find_one({"_id": chat_id})

    if not data:
        return [None, None]

    return [
        data.get("file_id"),
        data.get("caption")
    ]


def find_one(chat_id):
    return dbcol.find_one({"_id": chat_id})


# =========================
# 📢 ALL IDS
# =========================
def getid():
    return [user["_id"] for user in dbcol.find()]


def delete(id):
    dbcol.delete_one(id)


# =========================
# 🔥 REFERRAL SYSTEM
# =========================

def update_referral(user_id, referrer_id):
    user = dbcol.find_one({"_id": user_id})

    if not user:
        return

    # prevent duplicate referral
    if user.get("referred_by"):
        return

    if user_id == referrer_id:
        return

    # set referrer
    dbcol.update_one(
        {"_id": user_id},
        {"$set": {"referred_by": referrer_id}}
    )

    ref_user = dbcol.find_one({"_id": referrer_id})

    if not ref_user:
        return

    new_refs = ref_user.get("referrals", 0) + 1
    new_points = (new_refs // 3) * 10

    dbcol.update_one(
        {"_id": referrer_id},
        {"$set": {
            "referrals": new_refs,
            "points": new_points
        }}
    )


def get_referral_data(user_id):
    user = dbcol.find_one({"_id": user_id})
    if not user:
        return {"referrals": 0, "points": 0}

    return {
        "referrals": user.get("referrals", 0),
        "points": user.get("points", 0)
    }


def reset_points(user_id):
    dbcol.update_one({"_id": user_id}, {"$set": {"points": 0}})
