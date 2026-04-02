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


def send_publish(message: str) -> None:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.sendto(message.encode(), ("127.0.0.1", 5051))

    try:
        client_socket.settimeout(2)
        response, server_address = client_socket.recvfrom(4096)
        print(f"Sent: {message}")
        print(f"Server response: {response.decode()}")
        print(f"Server address: {server_address}")
        print()
    except socket.timeout:
        print(f"Sent: {message}")
        print("Server response: No response (success path for now)")
        print()

    client_socket.close()


bob_listener = threading.Thread(target=listen, args=("Bob", 6002))
bob_listener.start()

time.sleep(1)

send_publish("PUBLISH|1|Alice|sports|Big Match Tonight|The finals will be played at 8 PM.")

bob_listener.join()