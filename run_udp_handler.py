from client_server.config import SERVER_IP, UDP_PORT
from client_server.service import ServerService
from client_server.udp_handler import UDPServer


def main() -> None:
    service = ServerService()
    server = UDPServer(SERVER_IP, UDP_PORT, service)
    server.start()


if __name__ == "__main__":
    main()