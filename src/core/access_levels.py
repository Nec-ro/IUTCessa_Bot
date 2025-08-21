from collections import defaultdict
from telegram import Update
#import pickle
import json
import os

base_dir = os.path.dirname(__file__)
USER_ACCESS_PKL = os.path.join(base_dir, "user_access.pkl")
USER_ACCESS_JSON = os.path.join(base_dir, "user_access.json")

user_access = defaultdict(lambda: "user")

def load_user_access():
    global user_access
    if os.path.exists(USER_ACCESS_JSON):
        try:
            with open(USER_ACCESS_JSON, "r") as f:
                data = json.load(f)
                user_access = defaultdict(lambda: "user", {int(k): v for k, v in data.items()})
            print("User access level loaded successfully.")
            #print (f"ua: {user_access}")
        except Exception as e:
            print("Failed to load user access:", e)
        return user_access
    else:
        print("No existing access file found. Starting fresh.")

def save_user_access():
    with open(USER_ACCESS_JSON, "w") as f:
        json.dump({str(k): v for k, v in user_access.items()}, f, ensure_ascii=False, indent=2)

def get_user_access(user_id: int) -> str:
    return user_access.get(user_id, "user")

def set_user_access(user_id: int, access: str, update: Update):
    user_access[user_id] = access
    save_user_access()
    if update.message and update.message.from_user and update.message.from_user.username:
        print("@" + update.message.from_user.username + " reached access: " + access)

def user_access_keys():
    return user_access.keys()