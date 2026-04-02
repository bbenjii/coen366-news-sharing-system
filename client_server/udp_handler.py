import socket

from client_server.protocol import (
    build_comment,
    build_comment_denied,
    build_forward,
    build_forward_comment,
    build_message,
    build_publish_denied,
    parse_message,
)
from client_server.service import ServerService
from client_server.logger import log


class UDPServer:
    def __init__(
        self,
        host: str,
        port: int,
        service: ServerService,
        other_server_ip: str,
        other_server_udp_port: int,
    ) -> None:
        self.host = host
        self.port = port
        self.service = service
        self.other_server_ip = other_server_ip
        self.other_server_udp_port = other_server_udp_port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def start(self) -> None:
        self.server_socket.bind((self.host, self.port))
        log(f"UDP server listening on {self.host}:{self.port}")

        while True:
            data, client_address = self.server_socket.recvfrom(4096)
            raw_message = data.decode().strip()
            log(f"UDP received from {client_address}: {raw_message}")

            try:
                response = self.handle_request(raw_message)

                if response is not None and response != "":
                    self.server_socket.sendto(response.encode(), client_address)
                    log(f"UDP sent to {client_address}: {response}")
            except Exception as e:
                error_response = f"ERROR|{str(e)}"
                self.server_socket.sendto(error_response.encode(), client_address)
                log(f"UDP error for {client_address}: {error_response}")

    def handle_request(self, raw_message: str) -> str | None:
        parsed = parse_message(raw_message)
        command = parsed["command"]
        fields = parsed["fields"]

        if command == "PUBLISH":
            if len(fields) != 5:
                rq_id = fields[0] if len(fields) > 0 else "unknown"
                return build_publish_denied(rq_id, "Invalid PUBLISH format")

            rq_id, name, subject, title, text = fields
            name = name.strip()
            subject = subject.strip()
            title = title.strip()
            text = text.strip()

            if not name:
                return build_publish_denied(rq_id, "Empty username")

            if not subject:
                return build_publish_denied(rq_id, "Empty subject")

            if not title:
                return build_publish_denied(rq_id, "Empty title")

            if not text:
                return build_publish_denied(rq_id, "Empty text")

            success, message, recipients = self.service.publish_message(name, subject, title, text)

            if success:
                self.deliver_message_to_users(name, subject, title, text, recipients)
                self.forward_message_to_other_server(name, subject, title, text)
                return None

            return build_publish_denied(rq_id, message)

        if command == "PUBLISH-COMMENT":
            if len(fields) != 4:
                return build_comment_denied("Invalid PUBLISH-COMMENT format")

            name, subject, title, text = fields
            name = name.strip()
            subject = subject.strip()
            title = title.strip()
            text = text.strip()

            if not name:
                return build_comment_denied("Empty username")

            if not subject:
                return build_comment_denied("Empty subject")

            if not title:
                return build_comment_denied("Empty title")

            if not text:
                return build_comment_denied("Empty text")

            success, message, recipients = self.service.publish_comment(name, subject, title, text)

            if success:
                self.deliver_comment_to_users(name, subject, title, text, recipients)
                self.forward_comment_to_other_server(name, subject, title, text)
                return None

            return build_comment_denied(message)

        if command == "FORWARD":
            if len(fields) != 4:
                return "ERROR|Invalid FORWARD format"

            name, subject, title, text = fields
            self.service.remember_forwarded_message(name, subject, title, text)
            recipients = self.service.get_interested_users(subject)
            self.deliver_message_to_users(name, subject, title, text, recipients)
            return None

        if command == "FORWARD-COMMENT":
            if len(fields) != 4:
                return "ERROR|Invalid FORWARD-COMMENT format"

            name, subject, title, text = fields
            recipients = self.service.get_interested_users(subject)
            self.deliver_comment_to_users(name, subject, title, text, recipients)
            return None

        return "ERROR|Unsupported command"

    def deliver_message_to_users(
        self,
        name: str,
        subject: str,
        title: str,
        text: str,
        recipients: list,
    ) -> None:
        udp_message = build_message(name, subject.strip().lower(), title.strip(), text.strip())

        for user in recipients:
            target_address = (user.ip_address, user.udp_port)
            self.server_socket.sendto(udp_message.encode(), target_address)
            log(f"Delivered MESSAGE to {user.name} at {target_address}: {udp_message}")

    def deliver_comment_to_users(
        self,
        name: str,
        subject: str,
        title: str,
        text: str,
        recipients: list,
    ) -> None:
        udp_comment = build_comment(name, subject.strip().lower(), title.strip(), text.strip())

        for user in recipients:
            target_address = (user.ip_address, user.udp_port)
            self.server_socket.sendto(udp_comment.encode(), target_address)
            log(f"Delivered COMMENT to {user.name} at {target_address}: {udp_comment}")

    def forward_message_to_other_server(
        self,
        name: str,
        subject: str,
        title: str,
        text: str,
    ) -> None:
        forward_message = build_forward(name, subject.strip().lower(), title.strip(), text.strip())
        target_address = (self.other_server_ip, self.other_server_udp_port)
        self.server_socket.sendto(forward_message.encode(), target_address)
        log(f"Forwarded MESSAGE to other server at {target_address}: {forward_message}")

    def forward_comment_to_other_server(
        self,
        name: str,
        subject: str,
        title: str,
        text: str,
    ) -> None:
        forward_comment = build_forward_comment(name, subject.strip().lower(), title.strip(), text.strip())
        target_address = (self.other_server_ip, self.other_server_udp_port)
        self.server_socket.sendto(forward_comment.encode(), target_address)
        log(f"Forwarded COMMENT to other server at {target_address}: {forward_comment}")