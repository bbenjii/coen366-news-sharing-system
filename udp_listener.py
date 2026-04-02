import socket
import sys


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 udp_listener.py <name> <port>")
        return

    name = sys.argv[1]
    port = int(sys.argv[2])

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", port))

    print(f"{name} UDP listener running on 127.0.0.1:{port}")

    while True:
        data, addr = sock.recvfrom(4096)
        print(f"{name} received from {addr}: {data.decode()}")


if __name__ == "__main__":
    main()