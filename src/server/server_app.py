from src.server.tcp_server import TcpServer
from src.shared.config import SERVER_A
from src.server.udp_server import UdpServer
import threading


class ServerApp:
    def __init__(self, server_config=SERVER_A):
        self.server_config = server_config
        self.tcp_server = TcpServer(server_config)
        self.udp_server = UdpServer(server_config)



    def run(self):
        print("___Server has started___")
        threading.Thread(target=self.tcp_server.run).start()
        threading.Thread(target=self.udp_server.run).start()


def main():
    server = ServerApp()
    server.run()


if __name__ == "__main__":
    main()
