import json
from pathlib import Path


class ServerPersistence:
    def __init__(self, server_name):
        safe_server_name = server_name.lower().replace(" ", "_")
        self.file_path = Path("data") / f"{safe_server_name}_registrations.json"
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def load_users(self):
        if not self.file_path.exists():
            return {}

        with self.file_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def save_users(self, users_by_name):
        with self.file_path.open("w", encoding="utf-8") as file:
            json.dump(users_by_name, file, indent=2, sort_keys=True)
