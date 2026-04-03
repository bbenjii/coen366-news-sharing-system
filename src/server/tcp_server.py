import socket
import threading

from src.shared import protocol
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

        self.registered_users = self.persistence.load_users()
        if name in self.registered_users:
            print(f"[server] User {name} already registered")
            payload = protocol.serialize_register_denied(rq=register["request_id"], reason="name_already_taken")
            connection.sendall(payload.encode())
            return

        self.registered_users[name] = {
            "ip_address": register["ip_address"],
            "tcp_port": register["tcp_port"],
            "udp_port": register["udp_port"],
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
            elif command == b"DE-REGISTER":
                self.deregister_user(data)
            else:
                print(f"[server] Unsupported TCP command from {client_address}: {data.decode()}")
        finally:
            print(f"[server] Disconnected from {client_address}")
            connection.close()
    
