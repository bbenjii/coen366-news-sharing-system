import socket
import threading

from src.shared import protocol
from src.shared.models import (
    LoginConfirmedModel,
    LoginDeniedModel,
    SubjectsRejectedModel,
    SubjectsUpdatedModel,
    UpdateConfirmedModel,
    UpdateDeniedModel,
)
from src.server.persistence import ServerPersistence


class TcpServer:
    def __init__(self, server_config):
        self.server_config = server_config
        self.server_address = (server_config["bind_host"], server_config["tcp_port"])
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_socket.bind(self.server_address)
        self.client_threads = []
        
        self.persistence = ServerPersistence(server_config["name"])
        self.registered_users = self.persistence.load_users()

    def run(self):
        try:
            self.tcp_socket.listen(100)
            print("TCP Server is listening...")
            while True:
                connection, client_address = self.tcp_socket.accept()
                client_thread = threading.Thread(
                    target=self.handle_client_connection,
                    args=(connection, client_address),
                )
                client_thread.start()
                self.client_threads.append(client_thread)
        finally:
            print("Closing tcp server socket")
            for thread in self.client_threads:
                thread.join()
            self.tcp_socket.close()
    
    
    def register_user(self, connection, data):
        register = protocol.parse_register(data.decode())
        print(f"[server] Register request : {register}")
        name = register["name"]
        ip_address = register["ip_address"]
        tcp_port = register["tcp_port"]
        udp_port = register["udp_port"]

        self.registered_users = self.persistence.load_users()
        if name in self.registered_users:
            print(f"[server] User {name} already registered")
            payload = protocol.serialize_register_denied(rq=register["request_id"], reason="name_already_taken")
            connection.sendall(payload.encode())
            return

        if not protocol.is_valid_ip_address(ip_address):
            print(f"[server] Invalid IP address for registration: {ip_address}")
            payload = protocol.serialize_register_denied(
                rq=register["request_id"],
                reason="invalid_ip_address",
            )
            connection.sendall(payload.encode())
            return

        if not protocol.is_valid_port(tcp_port):
            print(f"[server] Invalid TCP port for registration: {tcp_port}")
            payload = protocol.serialize_register_denied(
                rq=register["request_id"],
                reason="invalid_tcp_port",
            )
            connection.sendall(payload.encode())
            return

        if not protocol.is_valid_port(udp_port):
            print(f"[server] Invalid UDP port for registration: {udp_port}")
            payload = protocol.serialize_register_denied(
                rq=register["request_id"],
                reason="invalid_udp_port",
            )
            connection.sendall(payload.encode())
            return

        for registered_name, registered_user in self.registered_users.items():
            if (
                registered_user["ip_address"] == ip_address
                and registered_user["tcp_port"] == tcp_port
            ):
                print(
                    f"[server] TCP endpoint already used by {registered_name}: "
                    f"{ip_address}:{tcp_port}"
                )
                payload = protocol.serialize_register_denied(
                    rq=register["request_id"],
                    reason="tcp_endpoint_in_use",
                )
                connection.sendall(payload.encode())
                return

            if (
                registered_user["ip_address"] == ip_address
                and registered_user["udp_port"] == udp_port
            ):
                print(
                    f"[server] UDP endpoint already used by {registered_name}: "
                    f"{ip_address}:{udp_port}"
                )
                payload = protocol.serialize_register_denied(
                    rq=register["request_id"],
                    reason="udp_endpoint_in_use",
                )
                connection.sendall(payload.encode())
                return

        self.registered_users[name] = {
            "ip_address": ip_address,
            "tcp_port": tcp_port,
            "udp_port": udp_port,
            "subjects": [],
        }
        self.persistence.save_users(self.registered_users)

        print(f"[server] User {name} registered")
        response = protocol.serialize_registered(register["request_id"])
        connection.sendall(response.encode())

    def deregister_user(self, data):
        deregister = protocol.parse_deregister(data.decode())
        print(f"[server] Deregister request: {deregister}")
        name = deregister["name"]

        self.registered_users = self.persistence.load_users()
        if name not in self.registered_users:
            print(f"[server] Ignoring deregistration for unknown user {name}")
            return

        del self.registered_users[name]
        self.persistence.save_users(self.registered_users)
        print(f"[server] User {name} deregistered")

    def login_user(self, connection, data):
        login = protocol.parse_login(data.decode())
        print(f"[server] Login request: {login}")
        name = login["name"]

        self.registered_users = self.persistence.load_users()
        if name not in self.registered_users:
            print(f"[server] Login denied for unknown user {name}")
            payload = protocol.serialize_login_denied(
                LoginDeniedModel(rq=str(login["request_id"]), reason="user_not_found")
            )
            connection.sendall(payload.encode())
            return

        user = self.registered_users[name]
        payload = protocol.serialize_login_confirmed(
            LoginConfirmedModel(
                rq=str(login["request_id"]),
                name=name,
                ip_address=user["ip_address"],
                tcp_port=user["tcp_port"],
                udp_port=user["udp_port"],
                subjects=user.get("subjects", []),
            )
        )
        print(f"[server] Login confirmed for {name}")
        connection.sendall(payload.encode())

    def update_user(self, connection, data):
        update = protocol.parse_update(data.decode())
        print(f"[server] Update request: {update}")
        name = update["name"]
        ip_address = update["ip_address"]
        tcp_port = update["tcp_port"]
        udp_port = update["udp_port"]

        self.registered_users = self.persistence.load_users()
        if name not in self.registered_users:
            print(f"[server] Update denied for unknown user {name}")
            payload = protocol.serialize_update_denied(
                UpdateDeniedModel(rq=str(update["request_id"]), reason="user_not_found")
            )
            connection.sendall(payload.encode())
            return

        if not protocol.is_valid_ip_address(ip_address):
            print(f"[server] Update denied for {name}: invalid IP address {ip_address}")
            payload = protocol.serialize_update_denied(
                UpdateDeniedModel(rq=str(update["request_id"]), reason="invalid_ip_address")
            )
            connection.sendall(payload.encode())
            return

        if not protocol.is_valid_port(tcp_port):
            print(f"[server] Update denied for {name}: invalid TCP port {tcp_port}")
            payload = protocol.serialize_update_denied(
                UpdateDeniedModel(rq=str(update["request_id"]), reason="invalid_tcp_port")
            )
            connection.sendall(payload.encode())
            return

        if not protocol.is_valid_port(udp_port):
            print(f"[server] Update denied for {name}: invalid UDP port {udp_port}")
            payload = protocol.serialize_update_denied(
                UpdateDeniedModel(rq=str(update["request_id"]), reason="invalid_udp_port")
            )
            connection.sendall(payload.encode())
            return

        for registered_name, registered_user in self.registered_users.items():
            if registered_name == name:
                continue

            if (
                registered_user["ip_address"] == ip_address
                and registered_user["tcp_port"] == tcp_port
            ):
                print(
                    f"[server] Update denied, TCP endpoint already used by {registered_name}: "
                    f"{ip_address}:{tcp_port}"
                )
                payload = protocol.serialize_update_denied(
                    UpdateDeniedModel(
                        rq=str(update["request_id"]),
                        reason="tcp_endpoint_in_use",
                    )
                )
                connection.sendall(payload.encode())
                return

            if (
                registered_user["ip_address"] == ip_address
                and registered_user["udp_port"] == udp_port
            ):
                print(
                    f"[server] Update denied, UDP endpoint already used by {registered_name}: "
                    f"{ip_address}:{udp_port}"
                )
                payload = protocol.serialize_update_denied(
                    UpdateDeniedModel(
                        rq=str(update["request_id"]),
                        reason="udp_endpoint_in_use",
                    )
                )
                connection.sendall(payload.encode())
                return

        self.registered_users[name] = {
            "ip_address": ip_address,
            "tcp_port": tcp_port,
            "udp_port": udp_port,
            "subjects": self.registered_users[name].get("subjects", []),
        }
        self.persistence.save_users(self.registered_users)
        print(f"[server] User {name} updated")
        payload = protocol.serialize_update_confirmed(
            UpdateConfirmedModel(
                rq=str(update["request_id"]),
                name=name,
                ip_address=ip_address,
                tcp_port=tcp_port,
                udp_port=udp_port,
                subjects=self.registered_users[name].get("subjects", []),
            )
        )
        connection.sendall(payload.encode())

    def update_subjects(self, connection, data):
        subjects_request = protocol.parse_subjects(data.decode())
        print(f"[server] Subjects request: {subjects_request}")
        name = subjects_request["name"]
        subjects = subjects_request["subjects"]

        self.registered_users = self.persistence.load_users()
        if name not in self.registered_users:
            print(f"[server] Subjects update rejected for unknown user {name}")
            payload = protocol.serialize_subjects_rejected(
                SubjectsRejectedModel(
                    rq=str(subjects_request["request_id"]),
                    name=name,
                    subjects=subjects,
                )
            )
            connection.sendall(payload.encode())
            return

        allowed_subjects = set(protocol.ALLOWED_SUBJECTS)
        if not subjects or any(subject not in allowed_subjects for subject in subjects):
            print(f"[server] Subjects update rejected for {name}: invalid subjects {subjects}")
            payload = protocol.serialize_subjects_rejected(
                SubjectsRejectedModel(
                    rq=str(subjects_request["request_id"]),
                    name=name,
                    subjects=subjects,
                )
            )
            connection.sendall(payload.encode())
            return

        self.registered_users[name]["subjects"] = subjects
        self.persistence.save_users(self.registered_users)
        print(f"[server] Subjects updated for {name}: {subjects}")
        payload = protocol.serialize_subjects_updated(
            SubjectsUpdatedModel(
                rq=str(subjects_request["request_id"]),
                name=name,
                subjects=subjects,
            )
        )
        connection.sendall(payload.encode())

    def handle_client_connection(self, connection, client_address):
        try:
            connection.sendall(b"hello")

            try:
                data = connection.recv(1024)
            except ConnectionResetError:
                print(f"[server] Connection reset by {client_address}")
                return

            if not data:
                return

            parts = data.strip().split()
            command = parts[0]

            if command == b"REGISTER":
                self.register_user(connection, data)
            elif command == b"LOGIN":
                self.login_user(connection, data)
            elif command == b"UPDATE":
                self.update_user(connection, data)
            elif command == b"SUBJECTS":
                self.update_subjects(connection, data)
            elif command == b"DE-REGISTER":
                self.deregister_user(data)
            else:
                print(f"[server] Unsupported TCP command from {client_address}: {data.decode()}")
        finally:
            print(f"[server] Disconnected from {client_address}")
            connection.close()
    
