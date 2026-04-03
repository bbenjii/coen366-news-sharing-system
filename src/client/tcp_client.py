import socket

from src.client import state
from src.client.state import ClientState
from src.shared import protocol
from src.shared.models import RegisterModel

class TcpClient:
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
        server_address = (server_config["bind_host"], server_config["tcp_port"])
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
                tcp_socket.connect(server_address)
                print("[client] Connected to server.")
                
                res = tcp_socket.recv(1024)
                if res != b"hello":
                    print(f"[client] Unexpected response from server: {res.decode()}")
                    return False
                
                # make register request
                register_payload = RegisterModel(rq="1", name=client_state.name, ip_address=client_state.ip_address, tcp_port=client_state.tcp_port, udp_port=client_state.udp_port)
                payload = protocol.serialize_register(register_payload)
                
                tcp_socket.sendall(payload.encode())
                
                res = tcp_socket.recv(1024)
                print(f"[client] Received response from server: {res.decode()}")
                
                
                
                # tcp_socket.sendall(message.encode())
                
                
                return True
        except ConnectionRefusedError:
            print(f"[client] Could not connect to {server_config['name']} at {server_address}")
        except OSError as exc:
            print(f"[client] TCP send failed: {exc}")
        
