import socket


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
