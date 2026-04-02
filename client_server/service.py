from client_server.logger import log
from client_server.models import Comment, NewsMessage, User
from client_server.storage import PersistentStorage
from client_server.config import ALLOWED_SUBJECTS


class ServerService:
    def __init__(self):
        self.storage = PersistentStorage()

    def register_user(self, name: str, ip_address: str, tcp_port: int, udp_port: int):
        users = self.storage.get_users()

        if name in users:
            return False, "Username already registered"

        user = User(
            name=name,
            ip_address=ip_address,
            tcp_port=tcp_port,
            udp_port=udp_port,
            subjects=[],
        )
        self.storage.save_user(user)
        log(f"User registered: {user}")
        return True, "Registered successfully"

    def deregister_user(self, name: str):
        users = self.storage.get_users()

        if name not in users:
            return False

        self.storage.delete_user(name)
        log(f"User deregistered: {name}")
        return True

    def user_exists(self, name: str) -> bool:
        users = self.storage.get_users()
        return name in users

    def update_user(self, name: str, ip_address: str, tcp_port: int, udp_port: int):
        users = self.storage.get_users()

        if name not in users:
            return False, "User not found"

        user = users[name]
        user.ip_address = ip_address
        user.tcp_port = tcp_port
        user.udp_port = udp_port

        self.storage.save_user(user)
        log(f"User updated: {user}")
        return True, "Updated successfully"

    def update_subjects(self, name: str, subjects: list[str]):
        users = self.storage.get_users()

        if name not in users:
            return False, "User not found"

        normalized_subjects = [subject.strip().lower() for subject in subjects if subject.strip()]
        allowed_subjects = {subject.lower() for subject in ALLOWED_SUBJECTS}

        invalid_subjects = [subject for subject in normalized_subjects if subject not in allowed_subjects]
        if invalid_subjects:
            return False, f"Invalid subjects: {','.join(invalid_subjects)}"

        user = users[name]
        user.subjects = normalized_subjects

        self.storage.save_user(user)
        log(f"Subjects updated for {name}: {normalized_subjects}")
        return True, "Subjects updated"

    def publish_message(self, sender: str, subject: str, title: str, text: str):
        users = self.storage.get_users()

        if sender not in users:
            return False, "Sender not registered", []

        normalized_subject = subject.strip().lower()
        normalized_title = title.strip()
        allowed_subjects = {item.lower() for item in ALLOWED_SUBJECTS}

        if normalized_subject not in allowed_subjects:
            return False, "Invalid subject", []

        sender_user = users[sender]
        sender_subjects = [item.strip().lower() for item in sender_user.subjects]

        if normalized_subject not in sender_subjects:
            return False, "Subject not in sender interests", []

        message = NewsMessage(
            sender=sender,
            subject=normalized_subject,
            title=normalized_title,
            text=text.strip(),
        )
        self.storage.save_message(message)
        log(f"Message published: {message}")

        recipients = [
            user
            for user in users.values()
            if normalized_subject in [item.strip().lower() for item in user.subjects]
        ]

        return True, "Published successfully", recipients

    def remember_forwarded_message(self, sender: str, subject: str, title: str, text: str):
        normalized_subject = subject.strip().lower()
        normalized_title = title.strip()

        if not self.message_exists(normalized_subject, normalized_title):
            message = NewsMessage(
                sender=sender,
                subject=normalized_subject,
                title=normalized_title,
                text=text.strip(),
            )
            self.storage.save_message(message)
            log(f"Forwarded message saved: {message}")

    def publish_comment(self, sender: str, subject: str, title: str, text: str):
        users = self.storage.get_users()

        if sender not in users:
            return False, "User not found", []

        normalized_subject = subject.strip().lower()
        normalized_title = title.strip()
        allowed_subjects = {item.lower() for item in ALLOWED_SUBJECTS}

        if normalized_subject not in allowed_subjects:
            return False, "Invalid subject", []

        if not self.message_exists(normalized_subject, normalized_title):
            return False, "Original message not found", []

        comment = Comment(
            sender=sender,
            subject=normalized_subject,
            title=normalized_title,
            text=text.strip(),
        )
        self.storage.save_comment(comment)
        log(f"Comment published: {comment}")

        recipients = [
            user
            for user in users.values()
            if normalized_subject in [item.strip().lower() for item in user.subjects]
        ]

        return True, "Comment published successfully", recipients

    def get_interested_users(self, subject: str):
        users = self.storage.get_users()
        normalized_subject = subject.strip().lower()

        return [
            user
            for user in users.values()
            if normalized_subject in [item.strip().lower() for item in user.subjects]
        ]

    def message_exists(self, subject: str, title: str) -> bool:
        normalized_subject = subject.strip().lower()
        normalized_title = title.strip().lower()

        return any(
            message.subject.strip().lower() == normalized_subject
            and message.title.strip().lower() == normalized_title
            for message in self.storage.get_messages()
        )