import socket


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
        print("Server response: No response")
        print()

    client_socket.close()


send_udp("FORWARD", 5061)
send_udp("FORWARD|Alice", 5061)
send_udp("FORWARD|Alice|sports", 5061)
send_udp("FORWARD|Alice|sports|Title", 5061)
send_udp("FORWARD|Alice|sports|Title|Text|extra", 5061)