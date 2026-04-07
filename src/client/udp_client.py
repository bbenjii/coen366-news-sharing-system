import socket
import threading

from src.client.state import ClientState
from src.shared import protocol
from src.shared.models import PublishCommentModel, PublishModel


class UdpClient:
    def __init__(self):
        self.listen_socket = None
        self.listen_thread = None
        self.running = False

    def start_listener(self, client_state: ClientState):
        udp_port = client_state.udp_port
        if udp_port is None:
            return

        try:
            udp_port = int(udp_port)
        except (TypeError, ValueError):
            print(f"[client] Cannot start UDP listener with invalid port: {udp_port}")
            return

        self.stop_listener()

        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_socket.bind(("0.0.0.0", udp_port))
        self.running = True
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()
        print(f"[client] UDP listener started on port {udp_port}")

    def stop_listener(self):
        self.running = False
        if self.listen_socket is not None:
            try:
                self.listen_socket.close()
            except OSError:
                pass
            self.listen_socket = None
        self.listen_thread = None

    def _listen_loop(self):
        while self.running and self.listen_socket is not None:
            try:
                data, sender = self.listen_socket.recvfrom(4096)
            except OSError:
                break

            raw_message = data.decode()
            print(f"[client] Received UDP from {sender}: {raw_message}")
            try:
                message = protocol.parse_udp_message(raw_message)
            except ValueError as exc:
                print(f"[client] Failed to parse UDP message: {exc}")
                continue

            command = message.get("command")
            if command == "MESSAGE":
                print(
                    f"[client] MESSAGE from {message['name']} "
                    f"on {message['subject']}: {message['title']} | {message['text']}"
                )
            elif command == "COMMENT":
                print(
                    f"[client] COMMENT from {message['name']} "
                    f"on {message['subject']} / {message['title']}: {message['text']}"
                )
            elif command == "PUBLISH-DENIED":
                print(
                    f"[client] Publish denied for request {message['request_id']}: "
                    f"{message['reason']}"
                )
            else:
                print(f"[client] Unsupported UDP message: {message}")

    def publish_news(self, server_config, client_state: ClientState, subject: str, title: str, text: str):
        server_address = (server_config["connect_host"], server_config["udp_port"])
        payload = protocol.serialize_publish(
            PublishModel(
                rq="1",
                name=client_state.name,
                subject=subject,
                title=title,
                text=text,
            )
        )

        try:
            if self.listen_socket is not None:
                print(f"[client] Sending UDP: {payload}")
                self.listen_socket.sendto(payload.encode(), server_address)
                return True

            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
                if client_state.udp_port is not None:
                    udp_socket.bind(("0.0.0.0", int(client_state.udp_port)))
                print(f"[client] Sending UDP: {payload}")
                udp_socket.sendto(payload.encode(), server_address)
                return True
        except OSError as exc:
            print(f"[client] UDP send failed: {exc}")
            return False

    def publish_comment(self, server_config, client_state: ClientState, subject: str, title: str, text: str):
        server_address = (server_config["connect_host"], server_config["udp_port"])
        payload = protocol.serialize_publish_comment(
            PublishCommentModel(
                name=client_state.name,
                subject=subject,
                title=title,
                text=text,
            )
        )

        try:
            if self.listen_socket is not None:
                print(f"[client] Sending UDP: {payload}")
                self.listen_socket.sendto(payload.encode(), server_address)
                return True

            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
                if client_state.udp_port is not None:
                    udp_socket.bind(("0.0.0.0", int(client_state.udp_port)))
                print(f"[client] Sending UDP: {payload}")
                udp_socket.sendto(payload.encode(), server_address)
                return True
        except OSError as exc:
            print(f"[client] UDP send failed: {exc}")
            return False
