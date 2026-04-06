import socket

from src.server.persistence import ServerPersistence
from src.shared import protocol
from src.shared.models import ForwardModel, MessageModel, PublishDeniedModel


class UdpServer:
    def __init__(self, server_config, peer_server_config=None):
        self.server_config = server_config
        self.peer_server_config = peer_server_config
        self.server_address = (server_config["bind_host"], server_config["udp_port"])
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_socket.bind(self.server_address)
        self.persistence = ServerPersistence(server_config["name"])

    def run(self):
        print(f"UDP Server is listening on {self.server_address}...")
        while True:
            data, sender_address = self.udp_socket.recvfrom(4096)
            raw_message = data.decode()
            print(f"[server] Received UDP from {sender_address}: {raw_message}")
            try:
                message = protocol.parse_udp_message(raw_message)
            except ValueError as exc:
                print(f"[server] Invalid UDP payload: {exc}")
                continue

            command = message.get("command")
            if command == "PUBLISH":
                self.handle_publish(message, sender_address)
            elif command == "FORWARD":
                self.handle_forward(message)
            else:
                print(f"[server] Unsupported UDP command: {message}")

    def handle_publish(self, message, sender_address):
        users = self.persistence.load_users()
        name = message["name"]
        subject = message["subject"]

        if name not in users:
            self.send_publish_denied(sender_address, message["request_id"], "user_not_found")
            return

        user = users[name]
        if subject not in protocol.ALLOWED_SUBJECTS:
            self.send_publish_denied(sender_address, message["request_id"], "invalid_subject")
            return

        if subject not in user.get("subjects", []):
            self.send_publish_denied(sender_address, message["request_id"], "subject_not_subscribed")
            return

        self.deliver_to_local_users(message["name"], subject, message["title"], message["text"])
        self.forward_to_peer(message["name"], subject, message["title"], message["text"])

    def handle_forward(self, message):
        self.deliver_to_local_users(message["name"], message["subject"], message["title"], message["text"])

    def deliver_to_local_users(self, name: str, subject: str, title: str, text: str):
        users = self.persistence.load_users()
        payload = protocol.serialize_message(
            MessageModel(name=name, subject=subject, title=title, text=text)
        )

        for username, user in users.items():
            if subject not in user.get("subjects", []):
                continue

            target_address = (user["ip_address"], int(user["udp_port"]))
            print(f"[server] Sending UDP to {username} at {target_address}: {payload}")
            self.udp_socket.sendto(payload.encode(), target_address)

    def forward_to_peer(self, name: str, subject: str, title: str, text: str):
        if not self.peer_server_config or not self.peer_server_config.get("connect_host"):
            return

        target_address = (
            self.peer_server_config["connect_host"],
            self.peer_server_config["udp_port"],
        )
        payload = protocol.serialize_forward(
            ForwardModel(name=name, subject=subject, title=title, text=text)
        )
        print(f"[server] Forwarding UDP to peer {target_address}: {payload}")
        self.udp_socket.sendto(payload.encode(), target_address)

    def send_publish_denied(self, sender_address, request_id, reason: str):
        payload = protocol.serialize_publish_denied(
            PublishDeniedModel(rq=str(request_id), reason=reason)
        )
        print(f"[server] Sending UDP deny to {sender_address}: {payload}")
        self.udp_socket.sendto(payload.encode(), sender_address)
