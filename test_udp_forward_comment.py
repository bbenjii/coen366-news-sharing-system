import socket
import threading
import time


def listen(name: str, port: int) -> None:
    listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listener.bind(("127.0.0.1", port))
    listener.settimeout(10)

    received_count = 0

    while received_count < 2:
        try:
            data, address = listener.recvfrom(4096)
            print(f"{name} received: {data.decode()}")
            print(f"{name} from: {address}")
            received_count += 1
        except socket.timeout:
            print(f"{name} timed out waiting for more messages.")
            break

    listener.close()


def send_udp(message: str, port: int) -> None:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.sendto(message.encode(), ("127.0.0.1", port))

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

send_udp("PUBLISH|1|Alice|sports|Big Match Tonight|The finals will be played at 8 PM.", 5051)
time.sleep(1)
send_udp("PUBLISH-COMMENT|Alice|sports|Big Match Tonight|I think this will be a great game.", 5051)

bob_listener.join()