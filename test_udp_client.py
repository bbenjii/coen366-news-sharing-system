import socket
from client_server import protocol

SERVER_A_IP = "127.0.0.1"
SERVER_A_UDP_PORT = 5051
SERVER_B_IP = "127.0.0.1"
SERVER_B_UDP_PORT = 5061

next_request_id = 100


def get_next_request_id() -> str:
    global next_request_id
    rq_id = str(next_request_id)
    next_request_id += 1
    return rq_id


def send_udp_message(message: str, server_ip: str, server_port: int) -> str | None:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(2)

    print(f"\nSent to {server_ip}:{server_port}: {message}")
    client_socket.sendto(message.encode(), (server_ip, server_port))

    try:
        response, addr = client_socket.recvfrom(4096)
        decoded = response.decode()
        print(f"Server response: {decoded}")
        print(f"From: {addr}")
        client_socket.close()
        return decoded
    except socket.timeout:
        print("Server response: [no response]")
        client_socket.close()
        return None


def prompt_non_empty(label: str) -> str:
    while True:
        value = input(label).strip()
        if value:
            return value
        print("Value cannot be empty.")


def choose_server() -> tuple[str, int]:
    choice = input("Server? (A/B): ").strip().upper()
    if choice == "B":
        return SERVER_B_IP, SERVER_B_UDP_PORT
    return SERVER_A_IP, SERVER_A_UDP_PORT


def publish_flow() -> None:
    name = prompt_non_empty("Publisher name: ")
    subject = prompt_non_empty("Subject: ")
    title = prompt_non_empty("Title: ")
    text = prompt_non_empty("Text: ")

    rq_id = get_next_request_id()
    server_ip, server_port = choose_server()

    print(f"Auto Request ID: {rq_id}")

    message = protocol.build_publish(rq_id, name, subject, title, text)
    send_udp_message(message, server_ip, server_port)


def comment_flow() -> None:
    name = prompt_non_empty("Commenter name: ")
    subject = prompt_non_empty("Original subject: ")
    title = prompt_non_empty("Original title: ")
    text = prompt_non_empty("Comment text: ")

    server_ip, server_port = choose_server()

    message = protocol.build_publish_comment(name, subject, title, text)
    send_udp_message(message, server_ip, server_port)


def menu() -> None:
    while True:
        print("\n=== UDP CLIENT MENU ===")
        print("1. Publish news")
        print("2. Publish comment")
        print("0. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            publish_flow()
        elif choice == "2":
            comment_flow()
        elif choice == "0":
            print("Exiting UDP client.")
            break
        else:
            print("Invalid choice.")


def main() -> None:
    menu()


if __name__ == "__main__":
    main()