import json
import socket
import threading

from src.shared import SERVER_A, SERVER_B


class ServerApp:
    def __init__(self, server_config=SERVER_A):
        self.server_config = server_config

        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_address = (server_config["bind_host"], server_config["tcp_port"])
        self.tcp_socket.bind(self.server_address)
        
        self.tcp_client_connection_threads = []
    
    def run(self):
        print("___Server has started___")
        
        # Start the TCP server
        self.start_tcp_socket()     

        
    
    def start_tcp_socket(self):
        try:
            # Listen for incoming connections
            self.tcp_socket.listen(100)  # Allow up to 4 connections
            print('TCP Server is listening...')
            while True:
                # Wait for a connection
                connection, client_address = self.tcp_socket.accept()

                # Create a thread for each client connection
                client_connection_thread = threading.Thread(target=self.handle_tcp_client_connection,
                                                            args=(connection, client_address))
                client_connection_thread.start()
                self.tcp_client_connection_threads.append(client_connection_thread)
                pass
        finally:
            print('Closing tcp server socket')

            for thread in self.tcp_client_connection_threads:
                thread.join()
                thread.close()
            self.tcp_socket.close()

    def handle_tcp_client_connection(self, connection, client_address):
        try:
            connection.sendall(b"hello")
            print(f"[server] Sent 'hello' to client")

            while True:
                data = connection.recv(1024)
                if data:
                    print(f"[server] Received '{data.decode()}' from client")

                else:
                    break


        finally:
            print(f"[server] Disconnected from {client_address}")
            connection.close()


def main():
    server = ServerApp()
    server.run()

if __name__ == '__main__':
    main()