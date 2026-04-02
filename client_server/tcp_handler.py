import ipaddress
import socket

from client_server import protocol
from client_server.config import ALLOWED_SUBJECTS, get_other_server_ip, ip_belongs_to_this_server
from client_server.logger import log
from client_server.service import ServerService


class TCPHandler:
    def __init__(self, host: str, port: int, service: ServerService):
        self.host = host
        self.port = port
        self.service = service

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen()

        log(f"TCP server listening on {self.host}:{self.port}")

        while True:
            conn, addr = server_socket.accept()
            log(f"TCP connection from {addr}")
            self.handle_client(conn)

    def handle_client(self, conn: socket.socket):
        with conn:
            raw_data = conn.recv(4096).decode()
            if not raw_data:
                return

            log(f"TCP received: {raw_data}")
            message = protocol.parse_message(raw_data)
            command = message["command"]
            fields = message["fields"]

            response = self.route_command(command, fields)

            if response:
                conn.sendall(response.encode())
                log(f"TCP sent: {response}")

    def route_command(self, command: str, fields: list[str]) -> str:
        if command == "REGISTER":
            return self.handle_register(fields)
        if command == "DE-REGISTER":
            return self.handle_deregister(fields)
        if command == "UPDATE":
            return self.handle_update(fields)
        if command == "SUBJECTS":
            return self.handle_subjects(fields)
        return "ERROR|Unknown command"

    def _is_valid_ip(self, ip_address: str) -> bool:
        try:
            ipaddress.ip_address(ip_address)
            return True
        except ValueError:
            return False

    def _is_valid_port(self, port: int) -> bool:
        return 1 <= port <= 65535

    def handle_register(self, fields: list[str]) -> str:
        if len(fields) != 5:
            rq_id = fields[0] if fields else "0"
            return protocol.build_register_denied(rq_id, "Invalid REGISTER format")

        rq_id, name, ip_address, tcp_port_str, udp_port_str = fields

        if not name.strip():
            return protocol.build_register_denied(rq_id, "Empty username")

        if not self._is_valid_ip(ip_address):
            return protocol.build_register_denied(rq_id, "Invalid IP address")

        try:
            tcp_port = int(tcp_port_str)
            udp_port = int(udp_port_str)
        except ValueError:
            return protocol.build_register_denied(rq_id, "Invalid port number")

        if not self._is_valid_port(tcp_port) or not self._is_valid_port(udp_port):
            return protocol.build_register_denied(rq_id, "Port out of valid range")

        if not ip_belongs_to_this_server(ip_address):
            return protocol.build_refer(rq_id, get_other_server_ip())

        success, reason = self.service.register_user(name, ip_address, tcp_port, udp_port)

        if success:
            return protocol.build_registered(rq_id)
        return protocol.build_register_denied(rq_id, reason)

    def handle_deregister(self, fields: list[str]) -> str:
        if len(fields) != 2:
            rq_id = fields[0] if fields else "0"
            return protocol.build_deregister_denied(rq_id, "Invalid DE-REGISTER format")

        rq_id, name = fields

        if not name.strip():
            return protocol.build_deregister_denied(rq_id, "Empty username")

        result = self.service.deregister_user(name)

        if result:
            return protocol.build_deregistered(rq_id)

        return ""

    def handle_update(self, fields: list[str]) -> str:
        if len(fields) != 5:
            rq_id = fields[0] if fields else "0"
            return protocol.build_update_denied(rq_id, "Invalid UPDATE format")

        rq_id, name, ip_address, tcp_port_str, udp_port_str = fields

        if not name.strip():
            return protocol.build_update_denied(rq_id, "Empty username")

        if not self._is_valid_ip(ip_address):
            return protocol.build_update_denied(rq_id, "Invalid IP address")

        try:
            tcp_port = int(tcp_port_str)
            udp_port = int(udp_port_str)
        except ValueError:
            return protocol.build_update_denied(rq_id, "Invalid port number")

        if not self._is_valid_port(tcp_port) or not self._is_valid_port(udp_port):
            return protocol.build_update_denied(rq_id, "Port out of valid range")

        if not self.service.user_exists(name):
            return protocol.build_update_denied(rq_id, "User not found")

        if not ip_belongs_to_this_server(ip_address):
            self.service.deregister_user(name)
            return protocol.build_refer(rq_id, get_other_server_ip())

        success, reason = self.service.update_user(name, ip_address, tcp_port, udp_port)

        if success:
            return protocol.build_update_confirmed(rq_id, name, ip_address, tcp_port, udp_port)
        return protocol.build_update_denied(rq_id, reason)

    def handle_subjects(self, fields: list[str]) -> str:
        if len(fields) != 3:
            rq_id = fields[0] if fields else "0"
            name = fields[1] if len(fields) > 1 else ""
            subjects = fields[2] if len(fields) > 2 else ""
            return protocol.build_subjects_rejected(rq_id, name, subjects, "Invalid SUBJECTS format")

        rq_id, name, subjects_csv = fields

        if not name.strip():
            return protocol.build_subjects_rejected(rq_id, name, subjects_csv, "Empty username")

        if not subjects_csv.strip():
            return protocol.build_subjects_rejected(rq_id, name, subjects_csv, "Empty subjects list")

        subjects = [subject.strip() for subject in subjects_csv.split(",") if subject.strip()]

        invalid_subjects = [subject for subject in subjects if subject not in ALLOWED_SUBJECTS]
        if invalid_subjects:
            return protocol.build_subjects_rejected(
                rq_id,
                name,
                subjects_csv,
                f"Invalid subjects: {','.join(invalid_subjects)}",
            )

        success, reason = self.service.update_subjects(name, subjects)

        if success:
            return protocol.build_subjects_updated(rq_id, name, ",".join(subjects))
        return protocol.build_subjects_rejected(rq_id, name, subjects_csv, reason)