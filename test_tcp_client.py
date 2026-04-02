import socket
from client_server import protocol

SERVER_A_IP = "127.0.0.1"
SERVER_A_TCP_PORT = 5050
SERVER_B_IP = "127.0.0.1"
SERVER_B_TCP_PORT = 5060

CLIENT_IP_A = "127.0.0.1"
CLIENT_IP_B = "127.0.0.2"

next_request_id = 1
next_tcp_port_a = 5001
next_udp_port_a = 6001
next_tcp_port_b = 7001
next_udp_port_b = 8001


def get_next_request_id() -> str:
    global next_request_id
    rq_id = str(next_request_id)
    next_request_id += 1
    return rq_id


def get_next_ports_for_server(server_choice: str) -> tuple[str, int, int]:
    global next_tcp_port_a, next_udp_port_a, next_tcp_port_b, next_udp_port_b

    if server_choice == "B":
        tcp_port = next_tcp_port_b
        udp_port = next_udp_port_b
        next_tcp_port_b += 1
        next_udp_port_b += 1
        return CLIENT_IP_B, tcp_port, udp_port

    tcp_port = next_tcp_port_a
    udp_port = next_udp_port_a
    next_tcp_port_a += 1
    next_udp_port_a += 1
    return CLIENT_IP_A, tcp_port, udp_port


def send_tcp_message(message: str, server_ip: str, server_port: int) -> str | None:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))

    print(f"\nSent to {server_ip}:{server_port}: {message}")
    client_socket.sendall(message.encode())

    try:
        response = client_socket.recv(4096).decode()
        if response:
            print(f"Server response: {response}")
            client_socket.close()
            return response

        print("Server response: [no response]")
        client_socket.close()
        return None

    except ConnectionResetError:
        print("Server response: [no response]")
        client_socket.close()
        return None


def prompt_non_empty(label: str) -> str:
    while True:
        value = input(label).strip()
        if value:
            return value
        print("Value cannot be empty.")


def choose_server() -> str:
    choice = input("Server? (A/B): ").strip().upper()
    if choice == "B":
        return "B"
    return "A"


def get_server_target(server_choice: str) -> tuple[str, int]:
    if server_choice == "B":
        return SERVER_B_IP, SERVER_B_TCP_PORT
    return SERVER_A_IP, SERVER_A_TCP_PORT


def register_flow() -> None:
    name = prompt_non_empty("Name: ")
    server_choice = choose_server()

    rq_id = get_next_request_id()
    ip_address, tcp_port, udp_port = get_next_ports_for_server(server_choice)
    server_ip, server_port = get_server_target(server_choice)

    print(f"Auto Request ID: {rq_id}")
    print(f"Auto IP: {ip_address}")
    print(f"Auto TCP Port: {tcp_port}")
    print(f"Auto UDP Port: {udp_port}")

    message = protocol.build_register(rq_id, name, ip_address, tcp_port, udp_port)
    send_tcp_message(message, server_ip, server_port)


def subjects_flow() -> None:
    name = prompt_non_empty("Name: ")
    subjects = prompt_non_empty("Subjects (comma-separated): ")
    server_choice = choose_server()

    rq_id = get_next_request_id()
    server_ip, server_port = get_server_target(server_choice)

    print(f"Auto Request ID: {rq_id}")

    message = protocol.build_subjects(rq_id, name, subjects)
    send_tcp_message(message, server_ip, server_port)


def update_flow() -> None:
    name = prompt_non_empty("Name: ")
    server_choice = choose_server()

    rq_id = get_next_request_id()
    ip_address, tcp_port, udp_port = get_next_ports_for_server(server_choice)
    server_ip, server_port = get_server_target("A")

    print(f"Auto Request ID: {rq_id}")
    print(f"Auto New IP: {ip_address}")
    print(f"Auto New TCP Port: {tcp_port}")
    print(f"Auto New UDP Port: {udp_port}")

    message = protocol.build_update(rq_id, name, ip_address, tcp_port, udp_port)
    response = send_tcp_message(message, server_ip, server_port)

    if response and response.startswith("REFER|"):
        referred_ip = response.split("|")[2]
        referred_port = SERVER_B_TCP_PORT if server_choice == "B" else SERVER_A_TCP_PORT

        register_message = protocol.build_register(rq_id, name, ip_address, tcp_port, udp_port)
        send_tcp_message(register_message, referred_ip, referred_port)


def deregister_flow() -> None:
    name = prompt_non_empty("Name: ")
    server_choice = choose_server()

    rq_id = get_next_request_id()
    server_ip, server_port = get_server_target(server_choice)

    print(f"Auto Request ID: {rq_id}")

    message = protocol.build_deregister(rq_id, name)
    send_tcp_message(message, server_ip, server_port)


def menu() -> None:
    while True:
        print("\n=== TCP CLIENT MENU ===")
        print("1. Register user")
        print("2. Update subjects")
        print("3. Update user address/ports")
        print("4. Deregister user")
        print("0. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            register_flow()
        elif choice == "2":
            subjects_flow()
        elif choice == "3":
            update_flow()
        elif choice == "4":
            deregister_flow()
        elif choice == "0":
            print("Exiting TCP client.")
            break
        else:
            print("Invalid choice.")


def main() -> None:
    menu()


if __name__ == "__main__":
    main()