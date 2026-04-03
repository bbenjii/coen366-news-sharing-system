from src.server.tcp_server import TcpServer
from src.shared.config import SERVER_A


class ServerApp:
    def __init__(self, server_config=SERVER_A):
        self.server_config = server_config
        self.tcp_server = TcpServer(server_config)

    def run(self):
        print("___Server has started___")
        self.tcp_server.run()


def main():
    server = ServerApp()
    server.run()


if __name__ == "__main__":
    main()
