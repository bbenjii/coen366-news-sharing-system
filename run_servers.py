import os
import threading

os.environ["SERVER_NAME"] = "ServerA"
os.environ["SERVER_IP"] = "127.0.0.1"
os.environ["TCP_PORT"] = "5050"
os.environ["UDP_PORT"] = "5051"
os.environ["OTHER_SERVER_NAME"] = "ServerB"
os.environ["OTHER_SERVER_IP"] = "127.0.0.1"
os.environ["OTHER_SERVER_TCP_PORT"] = "5060"
os.environ["OTHER_SERVER_UDP_PORT"] = "5061"

from client_server.config import SERVER_IP, TCP_PORT, UDP_PORT, OTHER_SERVER_IP, OTHER_SERVER_UDP_PORT
from client_server.logger import log
from client_server.service import ServerService
from client_server.tcp_handler import TCPHandler
from client_server.udp_handler import UDPServer


def main():
    service = ServerService()

    tcp_server = TCPHandler(SERVER_IP, TCP_PORT, service)
    udp_server = UDPServer(
        SERVER_IP,
        UDP_PORT,
        service,
        OTHER_SERVER_IP,
        OTHER_SERVER_UDP_PORT,
    )

    tcp_thread = threading.Thread(target=tcp_server.start, daemon=True)
    udp_thread = threading.Thread(target=udp_server.start, daemon=True)

    tcp_thread.start()
    udp_thread.start()

    log("Server A TCP and UDP servers are running.")

    try:
        while True:
            tcp_thread.join(timeout=1)
            udp_thread.join(timeout=1)

            if not tcp_thread.is_alive():
                log("Server A TCP thread stopped.")
                break

            if not udp_thread.is_alive():
                log("Server A UDP thread stopped.")
                break
    except KeyboardInterrupt:
        log("Server A stopped.")


if __name__ == "__main__":
    main()