import socket

from src.client.state import ClientState
from src.shared import protocol
from src.shared.models import DeregisterModel, RegisterModel

class TcpClient:
    @staticmethod
    def _open_connection(server_config):
        server_address = (server_config["bind_host"], server_config["tcp_port"])
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.connect(server_address)
        print("[client] Connected to server.")
        res = tcp_socket.recv(1024)
        if res != b"hello":
            tcp_socket.close()
            raise OSError(f"Unexpected response from server: {res.decode()}")
        return tcp_socket

    def send_message(self, server_config, message):
        server_address = (server_config["bind_host"], server_config["tcp_port"])

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
                tcp_socket.connect(server_address)
                print("[client] Connected to server.")
                tcp_socket.sendall(message.encode())
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
                tcp_socket.sendall(payload.encode())

                res = tcp_socket.recv(1024)
                print(f"[client] Received response from server: {res.decode()}")
                return True
        except ConnectionRefusedError:
            server_address = (server_config["bind_host"], server_config["tcp_port"])
            print(f"[client] Could not connect to {server_config['name']} at {server_address}")
        except OSError as exc:
            print(f"[client] TCP send failed: {exc}")
        return False

    def deregister_user(self, server_config, client_state: ClientState):
        try:
            with self._open_connection(server_config) as tcp_socket:
                deregister_payload = DeregisterModel(rq="1", name=client_state.name)
                payload = protocol.serialize_deregister(deregister_payload)
                tcp_socket.sendall(payload.encode())

                res = tcp_socket.recv(1024)
                if res:
                    print(f"[client] Unexpected response from server: {res.decode()}")
                    return False

                print(f"[client] Deregistration request completed for {client_state.name}")
                return True
        except ConnectionRefusedError:
            server_address = (server_config["bind_host"], server_config["tcp_port"])
            print(f"[client] Could not connect to {server_config['name']} at {server_address}")
        except OSError as exc:
            print(f"[client] TCP send failed: {exc}")
        return False
