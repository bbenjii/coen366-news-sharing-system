import socket

from client_server import protocol

SERVER_IP = "127.0.0.1"
SERVER_TCP_PORT = 5060


def send_tcp_message(message: str):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, SERVER_TCP_PORT))
    client_socket.sendall(message.encode())

    response = client_socket.recv(4096).decode()
    client_socket.close()

    print(f"Sent: {message}")
    print(f"Server response: {response}")
    print()


def main():
    messages = [
        protocol.build_register("1", "Bob", "127.0.0.2", 5002, 6002),
        protocol.build_subjects("2", "Bob", "sports,news"),
        protocol.build_update("3", "Bob", "127.0.0.2", 5004, 6004),
        protocol.build_deregister("4", "Bob"),
    ]

    for message in messages:
        send_tcp_message(message)


if __name__ == "__main__":
    main()