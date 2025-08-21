from telegram import Update
from collections import defaultdict
#import pickle
import json
import os

base_dir = os.path.dirname(__file__)
USER_STATES_PKL = os.path.join(base_dir, "user_states.pkl")
USER_STATES_JSON = os.path.join(base_dir, "user_states.json")

USER_STATES = { # FSM (for user state)
    "main-menu",
    "kmk-yar-main", "kmk-yar-get-link",
    "tech-stack-main", "tech-stack-first-forum", "tech-stack-user-info-confirm",
    "tech-stack-decision", "tech-stack-see-info", "tech-stack-pay", "tech-stack-vid-task",
    "backdoor-panel-head", "backdoor-panel", "backdoor-access-denied" ,
    "admin-list", "admin-add", "admin-remove",
    "registrant-panel", "registrant-edit", "registrant-edit-input", "registrant-remove", "registrant-remove-confirm",
    "interview-panel", "interviewee-accept", "interviewee-remove", "interviewee-reject",
    "pay-panel", "pay-list", "payer-add", "payer-remove",
    "filter-panel", "message-panel", "broadcast-confirm", "search-choose", "search-confirm", "user-search",
    "uploading-stage",
    "tech-stack-remind", "remind-add", "remind-remove",
    "tech-stack-priority", "priority-remove-confirm", "priority-selection-confirm",
    "priority-selection-course-1", "priority-selection-course-2", "priority-selection-course-3",
    "stats-panel", "user-stats-interests", "user-stats-priorities", "user-stats-results"
}

KMKYAR_MENUS = {
    "kmk-yar-main", "kmk-yar-get-link"
}

TECH_STACK_USER_PANEL = {
    "tech-stack-main", "tech-stack-first-forum", "tech-stack-user-info-confirm",
    "tech-stack-decision", "tech-stack-pay", "tech-stack-vid-task",
    "tech-stack-remind", "remind-add", "remind-remove",
    "tech-stack-priority", "priority-remove-confirm", "priority-selection-confirm",
    "priority-selection-course-1", "priority-selection-course-2", "priority-selection-course-3"
}

TECH_STACK_ADMIN_PANEL = {
    "backdoor-panel-head", "backdoor-panel", "backdoor-access-denied" ,
    "admin-list", "admin-add", "admin-remove",
    "registrant-panel", "registrant-edit", "registrant-edit-input", "registrant-remove", "registrant-remove-confirm",
    "interview-panel", "interviewee-accept", "interviewee-remove", "interviewee-reject",
    "pay-panel", "pay-list", "payer-add", "payer-remove",
    "uploading-stage",
    "filter-panel", "message-panel", "broadcast-confirm", "search-choose", "search-confirm", "user-search",
    "stats-panel", "user-stats-interests", "user-stats-priorities", "user-stats-results"
}

user_states = defaultdict(lambda: "main-menu") #default state

def load_user_state():
    global user_states
    '''
    try:
        with open(USER_STATES_PKL, "rb") as f:
            user_states = defaultdict(lambda: "main-menu", pickle.load(f))
        print("User states loaded successfully.")
    except FileNotFoundError:
        print("No existing state file found. Starting fresh.")
        user_states = defaultdict(lambda: "main-menu")
    '''
    if os.path.exists(USER_STATES_JSON):
        try:
            with open(USER_STATES_JSON, "r") as f:
                data = json.load(f)
                user_states = defaultdict(lambda: "main-menu", {int(k): v for k, v in data.items()})
            print("User state level loaded successfully.")
        except Exception as e:
            print("Failed to load user state:", e)
    else:
        print("No existing state file found. Starting fresh.")

def save_user_state():
    with open(USER_STATES_JSON, "w") as f:
        json.dump({str(k): v for k, v in user_states.items()}, f, ensure_ascii=False, indent=2)
    #with open("user_states.pkl", "wb") as f:
    #    pickle.dump(dict(user_states), f)

def get_user_state(user_id: int) -> str:
    return user_states[user_id]

def set_user_state(user_id: int, state: str, update: Update):
    user_states[user_id] = state
    if update.message and update.message.from_user and update.message.from_user.username:
        print("@" + update.message.from_user.username + " reached state: " + state)
