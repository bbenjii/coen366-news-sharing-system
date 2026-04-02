from client_server.config import SERVER_IP, TCP_PORT
from client_server.service import ServerService
from client_server.tcp_handler import TCPServer


def main() -> None:
    service = ServerService()
    server = TCPServer(SERVER_IP, TCP_PORT, service)
    server.start()


if __name__ == "__main__":
    main()