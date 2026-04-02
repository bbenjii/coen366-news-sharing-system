import json
import os

from client_server.config import STATE_FILE
from client_server.models import Comment, NewsMessage, User


class PersistentStorage:
    def __init__(self, filepath: str = STATE_FILE):
        self.filepath = filepath
        self.data = {
            "users": {},
            "messages": [],
            "comments": [],
        }
        self.load()

    def load(self):
        if not os.path.exists(self.filepath):
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            self.save()
            return

        with open(self.filepath, "r", encoding="utf-8") as file:
            raw = json.load(file)

        self.data["users"] = {
            name: User(**user_data)
            for name, user_data in raw.get("users", {}).items()
        }
        self.data["messages"] = [
            NewsMessage(**message_data)
            for message_data in raw.get("messages", [])
        ]
        self.data["comments"] = [
            Comment(**comment_data)
            for comment_data in raw.get("comments", [])
        ]

    def save(self):
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)

        serializable = {
            "users": {
                name: user.__dict__
                for name, user in self.data["users"].items()
            },
            "messages": [message.__dict__ for message in self.data["messages"]],
            "comments": [comment.__dict__ for comment in self.data["comments"]],
        }

        with open(self.filepath, "w", encoding="utf-8") as file:
            json.dump(serializable, file, indent=4)

    def get_users(self):
        return self.data["users"]

    def get_messages(self):
        return self.data["messages"]

    def get_comments(self):
        return self.data["comments"]

    def save_user(self, user: User):
        self.data["users"][user.name] = user
        self.save()

    def delete_user(self, name: str):
        if name in self.data["users"]:
            del self.data["users"][name]
            self.save()

    def save_message(self, message: NewsMessage):
        self.data["messages"].append(message)
        self.save()

    def save_comment(self, comment: Comment):
        self.data["comments"].append(comment)
        self.save()