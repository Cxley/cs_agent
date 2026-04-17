import json
import os

MEMORY_FILE = "memory_store.json"


def _load_store():
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)


def _save_store(store):
    with open(MEMORY_FILE, "w") as f:
        json.dump(store, f, indent=2)


def get_user(user_id):
    store = _load_store()
    if user_id not in store:
        store[user_id] = {
            "name": None,
            "orders": [],
            "history": []
        }
        _save_store(store)
    return store[user_id]


def save_user(user_id, user_data):
    store = _load_store()
    store[user_id] = user_data
    _save_store(store)
