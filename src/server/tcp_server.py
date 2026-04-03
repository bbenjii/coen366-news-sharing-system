import socket
import threading


class TcpServer:
    def __init__(self, server_config):
        self.server_config = server_config
        self.server_address = (server_config["bind_host"], server_config["tcp_port"])
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_socket.bind(self.server_address)
        self.client_threads = []

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

    @staticmethod
    def handle_client_connection(connection, client_address):
        try:
            connection.sendall(b"hello")
            print("[server] Sent 'hello' to client")

            while True:
                try:
                    data = connection.recv(1024)
                except ConnectionResetError:
                    print(f"[server] Connection reset by {client_address}")
                    break
                if not data:
                    break
                print(f"[server] Received '{data.decode()}' from client")
        finally:
            print(f"[server] Disconnected from {client_address}")
            connection.close()
