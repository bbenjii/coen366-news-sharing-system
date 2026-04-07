import socket

from src.client.state import ClientState
from src.shared import protocol
from src.shared.models import (
    DeregisterModel,
    LoginModel,
    RegisterModel,
    SubjectsModel,
    UpdateModel,
)

class TcpClient:
    @staticmethod
    def _open_connection(server_config):
        server_address = (server_config["connect_host"], server_config["tcp_port"])
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.connect(server_address)
        print("[client] Connected to server.")
        res = tcp_socket.recv(1024)
        if res != b"hello":
            tcp_socket.close()
            raise OSError(f"Unexpected response from server: {res.decode()}")
        return tcp_socket

    @staticmethod
    def _send_payload(tcp_socket, payload: str):
        print(f"[client] Sending: {payload}")
        tcp_socket.sendall(payload.encode())

    def send_message(self, server_config, message):
        server_address = (server_config["connect_host"], server_config["tcp_port"])

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
                tcp_socket.connect(server_address)
                print("[client] Connected to server.")
                self._send_payload(tcp_socket, message)
                return True
        except ConnectionRefusedError:
            print(f"[client] Could not connect to {server_config['name']} at {server_address}")
        except OSError as exc:
            print(f"[client] TCP send failed: {exc}")

        return False
    
    def register_user(self, server_config, client_state: ClientState):
        try:
            with self._open_connection(server_config) as tcp_socket:
                register_payload = RegisterModel(rq="1", name=client_state.name, ip_address=client_state.ip_address, tcp_port=client_state.tcp_port, udp_port=client_state.udp_port)
                payload = protocol.serialize_register(register_payload)
                self._send_payload(tcp_socket, payload)

                res = tcp_socket.recv(1024)
                response = res
                # print(f"[client] Received response from server: {response.decode()}")
                parts = response.strip().split()
                command = parts[0].decode()
                print(command)
                if command == "REGISTER-DENIED":
                    register_denied = protocol.parse_register_denied(response.decode())
                    print(f"[client] Registration denied: {register_denied['reason']}")
                    return False
                
                return command == "REGISTERED"
            
        except ConnectionRefusedError:
            server_address = (server_config["connect_host"], server_config["tcp_port"])
            print(f"[client] Could not connect to {server_config['name']} at {server_address}")
        except OSError as exc:
            print(f"[client] TCP send failed: {exc}")
        return False

    def deregister_user(self, server_config, client_state: ClientState):
        try:
            with self._open_connection(server_config) as tcp_socket:
                deregister_payload = DeregisterModel(rq="1", name=client_state.name)
                payload = protocol.serialize_deregister(deregister_payload)
                self._send_payload(tcp_socket, payload)

                res = tcp_socket.recv(1024)
                if res:
                    print(f"[client] Unexpected response from server: {res.decode()}")
                    return False

                print(f"[client] Deregistration request completed for {client_state.name}")
                return True
        except ConnectionRefusedError:
            server_address = (server_config["connect_host"], server_config["tcp_port"])
            print(f"[client] Could not connect to {server_config['name']} at {server_address}")
        except OSError as exc:
            print(f"[client] TCP send failed: {exc}")
        return False

    def login_user(self, server_config, name: str):
        try:
            with self._open_connection(server_config) as tcp_socket:
                login_payload = LoginModel(rq="1", name=name)
                payload = protocol.serialize_login(login_payload)
                self._send_payload(tcp_socket, payload)

                res = tcp_socket.recv(1024)
                response = res.decode()
                print(f"[client] Received response from server: {response}")
                command = response.strip().split()[0]

                if command == "LOGIN-DENIED":
                    login_denied = protocol.parse_login_denied(response)
                    print(f"[client] Login denied: {login_denied['reason']}")
                    return None

                if command != "LOGIN-CONFIRMED":
                    print(f"[client] Unexpected login response: {response}")
                    return None

                return protocol.parse_login_confirmed(response)
        except ConnectionRefusedError:
            server_address = (server_config["connect_host"], server_config["tcp_port"])
            print(f"[client] Could not connect to {server_config['name']} at {server_address}")
        except OSError as exc:
            print(f"[client] TCP send failed: {exc}")
        return None

    def update_user(self, server_config, client_state: ClientState):
        try:
            with self._open_connection(server_config) as tcp_socket:
                update_payload = UpdateModel(
                    rq="1",
                    name=client_state.name,
                    ip_address=client_state.ip_address,
                    tcp_port=client_state.tcp_port,
                    udp_port=client_state.udp_port,
                )
                payload = protocol.serialize_update(update_payload)
                self._send_payload(tcp_socket, payload)

                res = tcp_socket.recv(1024)
                response = res.decode()
                print(f"[client] Received response from server: {response}")
                command = response.strip().split()[0]

                if command == "UPDATE-DENIED":
                    update_denied = protocol.parse_update_denied(response)
                    print(f"[client] Update denied: {update_denied['reason']}")
                    return None

                if command != "UPDATE-CONFIRMED":
                    print(f"[client] Unexpected update response: {response}")
                    return None

                return protocol.parse_update_confirmed(response)
        except ConnectionRefusedError:
            server_address = (server_config["connect_host"], server_config["tcp_port"])
            print(f"[client] Could not connect to {server_config['name']} at {server_address}")
        except OSError as exc:
            print(f"[client] TCP send failed: {exc}")
        return None

    def update_subjects(self, server_config, client_state: ClientState):
        try:
            with self._open_connection(server_config) as tcp_socket:
                subjects_payload = SubjectsModel(
                    rq="1",
                    name=client_state.name,
                    subjects=client_state.subjects or [],
                )
                payload = protocol.serialize_subjects(subjects_payload)
                self._send_payload(tcp_socket, payload)

                res = tcp_socket.recv(1024)
                response = res.decode()
                print(f"[client] Received response from server: {response}")
                command = response.strip().split()[0]

                if command == "SUBJECTS-REJECTED":
                    subjects_rejected = protocol.parse_subjects_rejected(response)
                    print(
                        "[client] Subjects update rejected: "
                        f"{subjects_rejected['subjects'] or 'invalid request'}"
                    )
                    return None

                if command != "SUBJECTS-UPDATED":
                    print(f"[client] Unexpected subjects response: {response}")
                    return None

                return protocol.parse_subjects_updated(response)
        except ConnectionRefusedError:
            server_address = (server_config["connect_host"], server_config["tcp_port"])
            print(f"[client] Could not connect to {server_config['name']} at {server_address}")
        except OSError as exc:
            print(f"[client] TCP send failed: {exc}")
        return None
