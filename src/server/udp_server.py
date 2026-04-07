import socket
from src.server.persistence import ServerPersistence
from src.shared import protocol
from src.shared.config import SERVER_A, SERVER_B



class UdpServer:
    def __init__(self, server_config):
        self.server_config = server_config
        self.address = (server_config["bind_host"], server_config["udp_port"])
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.persistence = ServerPersistence(server_config["name"])

    def run(self):
        self.socket.bind(self.address)
        print(f"[UDP SERVER] Listening on {self.address}")

        while True:
            try:
                data, addr = self.socket.recvfrom(4096)
            except ConnectionResetError:
                continue
            message = data.decode()

            print(f"[UDP SERVER] Received: {message}")

            if message.startswith("PUBLISH-COMMENT"):
                self.handle_comment(message, addr)

            elif message.startswith("PUBLISH"):
                self.handle_publish(message, addr)

            elif message.startswith("FORWARD"):
                self.handle_forward(message)

    def handle_publish(self, message, addr):
        publish = protocol.parse_publish(message)

        if publish is None:
            print("[UDP SERVER] Invalid PUBLISH format")
            return

        users = self.persistence.load_users()

        name = publish["name"]
        subject = publish["subject"]
        rq = publish["request_id"]



        # USER NOT REGISTERED
        if name not in users:
            self.send_publish_denied(addr, rq, "user_not_registered")
            return

        # SUBJECT NOT IN USER INTERESTS
        if subject not in users[name].get("subjects", []):
            self.send_publish_denied(addr, rq, "subject_not_allowed")
            return


        for username, user in users.items():
            if subject in user.get("subjects", []):
                self.send_message(user, publish)


        self.forward_to_other_server(publish)

    def send_message(self, user, publish):
        msg = protocol.serialize_message(
            publish["name"],
            publish["subject"],
            publish["title"],
            publish["text"],
        )

        try:
            self.socket.sendto(
                msg.encode(),
                (user["ip_address"], int(user["udp_port"]))
            )
        except ConnectionResetError:
            print(f"[UDP SERVER] User not reachable → skipping")

        print(f"[UDP SERVER] Sent MESSAGE to {user['ip_address']}:{user['udp_port']}")

    def forward_to_other_server(self, publish):


        other_server = SERVER_B if self.server_config["name"] == "Server A" else SERVER_A

        message = f"FORWARD {publish['name']} {publish['subject']} {publish['title']} {publish['text']}"

        self.socket.sendto(
            message.encode(),
            (other_server["bind_host"], other_server["udp_port"])
        )

        print(f"[UDP SERVER] Forwarded to {other_server['name']}")

    def handle_forward(self, message):
        parts = message.strip().split(maxsplit=4)

        publish = {
            "name": parts[1],
            "subject": parts[2],
            "title": parts[3],
            "text": parts[4],
        }

        users = self.persistence.load_users()

        for username, user in users.items():
            if publish["subject"] in user.get("subjects", []):
                self.send_message(user, publish)

    def handle_comment(self, message):
        comment = protocol.parse_publish_comment(message)

        if comment is None:
            print("[UDP SERVER] Invalid COMMENT format")
            return

        if comment is None:
            print("[UDP SERVER] Invalid COMMENT format")
            return

        users = self.persistence.load_users()

        subject = comment["subject"]

        # Send to all interested users
        for username, user in users.items():
            if subject in user.get("subjects", []):
                self.send_comment(user, comment)

        # Forward to other server
        self.forward_comment(comment)

    def send_comment(self, user, comment):
        msg = protocol.serialize_comment(
            comment["name"],
            comment["subject"],
            comment["title"],
            comment["text"],
        )

        try:
            self.socket.sendto(
                msg.encode(),
                (user["ip_address"], int(user["udp_port"]))
            )
            print(f"[UDP SERVER] Sent COMMENT to {user['ip_address']}:{user['udp_port']}")
        except ConnectionResetError:
            print(f"[UDP SERVER] Skipped unreachable user")

    def forward_comment(self, comment):
        from src.shared.config import SERVER_A, SERVER_B

        other_server = SERVER_B if self.server_config["name"] == "Server A" else SERVER_A

        message = f"PUBLISH-COMMENT {comment['name']} {comment['subject']} {comment['title']} {comment['text']}"

        self.socket.sendto(
            message.encode(),
            (other_server["bind_host"], other_server["udp_port"])
        )

        print(f"[UDP SERVER] Forwarded COMMENT to {other_server['name']}")

    def send_publish_denied(self, addr, rq, reason):
        msg = protocol.serialize_publish_denied(rq, reason)

        self.socket.sendto(msg.encode(), addr)

        print(f"[UDP SERVER] Sent PUBLISH-DENIED to {addr}: {reason}")