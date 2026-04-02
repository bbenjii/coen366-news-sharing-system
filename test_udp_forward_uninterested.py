import socket
import threading
import time


def listen(name: str, port: int) -> None:
    listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listener.bind(("127.0.0.1", port))
    listener.settimeout(8)

    try:
        data, address = listener.recvfrom(4096)
        print(f"{name} received: {data.decode()}")
        print(f"{name} from: {address}")
    except socket.timeout:
        print(f"{name} received nothing.")

    listener.close()


def send_tcp(message: str, port: int) -> None:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("127.0.0.1", port))
    client_socket.sendall(message.encode())

    response = client_socket.recv(4096).decode()
    print(f"Sent TCP: {message}")
    print(f"Server response: {response}")
    print()

    client_socket.close()


def send_udp(message: str, port: int) -> None:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.sendto(message.encode(), ("127.0.0.1", port))

    try:
        client_socket.settimeout(2)
        response, server_address = client_socket.recvfrom(4096)
        print(f"Sent UDP: {message}")
        print(f"Server response: {response.decode()}")
        print(f"Server address: {server_address}")
        print()
    except socket.timeout:
        print(f"Sent UDP: {message}")
        print("Server response: No response (success path for now)")
        print()

    client_socket.close()


# Register Charlie on ServerB with a subject that is NOT sports
send_tcp("REGISTER|10|Charlie|127.0.0.1|5003|6003", 5060)
send_tcp("SUBJECTS|11|Charlie|health", 5060)

# Start listeners on ServerB side
bob_listener = threading.Thread(target=listen, args=("Bob", 6002))
charlie_listener = threading.Thread(target=listen, args=("Charlie", 6003))

bob_listener.start()
charlie_listener.start()

time.sleep(1)

# Publish sports from ServerA
send_udp("PUBLISH|12|Alice|sports|Cross Server Test|Only sports subscribers should receive this.", 5051)

bob_listener.join()
charlie_listener.join()