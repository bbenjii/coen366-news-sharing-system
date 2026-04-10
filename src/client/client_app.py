from src.client.state import ClientState
from src.client.tcp_client import TcpClient
from src.client.udp_client import UdpClient
from src.shared.config import ALLOWED_SUBJECTS, SERVER_A, SERVER_B, get_local_ip
from src.shared import protocol


class ClientApp:
    def __init__(self, name=None, server=None):
        self.local_ip = get_local_ip()
        print(f"Local IP: {self.local_ip}")
        self.state = ClientState(
            name=name,
            server=server,
            rq="REGISTER",
            ip_address=self.local_ip,
            subjects=[],
        )
        self.tcp_client = TcpClient()
        self.udp_client = UdpClient()

    def run(self):
        print("___Client has started___")

        if self.state.server is None:
            self.state.server = self.ask_user_server()

        print(f"Server set to {self.state.server['name']}")
        self.print_server_summary()

        if self.state.name is None:
            self.authenticate_user()
        else:
            login_info = self.tcp_client.login_user(self.state.server, self.state.name)
            if login_info is None:
                print("Failed to login, please authenticate yourself")
                self.authenticate_user()
            else:
                self.state.name = login_info["name"]
                self.state.ip_address = login_info["ip_address"]
                self.state.tcp_port = login_info["tcp_port"]
                self.state.udp_port = login_info["udp_port"]
                self.state.subjects = login_info["subjects"]
                self.udp_client.start_listener(self.state)

        print(f"Hi, {self.state.name}!")

        while True:
            self.handle_command()

    def authenticate_user(self):
        while True:
            print("Hi, please authenticate yourself:")
            print("commands: /login  /register")
            command = input(">> ").lower().strip()
            command = command[1:] if command.startswith("/") else command

            if command == "login":
                name = self.ask_user_name()
                login_info = self.tcp_client.login_user(self.state.server, name)
                if login_info is None:
                    continue

                self.state.name = login_info["name"]
                self.state.ip_address = login_info["ip_address"]
                self.state.tcp_port = login_info["tcp_port"]
                self.state.udp_port = login_info["udp_port"]
                self.state.subjects = login_info["subjects"]
                self.udp_client.start_listener(self.state)
                return

            if command == "register":
                self.state.name = self.ask_user_name()

                #  IP validation
                while True:
                    ip = self.ask_user_ip_address(default=self.state.ip_address)
                    if protocol.is_valid_ip_address(ip):
                        break
                    else:
                        print("Invalid IP address, try again.")

                #  TCP port validation
                while True:
                    tcp_port = self.ask_user_tcp_port()

                    if str(tcp_port).isdigit() and 1 <= int(tcp_port) <= 65535:
                        tcp_port = int(tcp_port)
                        break
                    else:
                        print("Invalid TCP port, try again.")

                #  UDP port validation
                while True:
                    udp_port = self.ask_user_udp_port()

                    if str(udp_port).isdigit() and 1 <= int(udp_port) <= 65535:
                        udp_port = int(udp_port)
                        break
                    else:
                        print("Invalid UDP port, try again.")

                self.state.ip_address = ip
                self.state.tcp_port = tcp_port
                self.state.udp_port = udp_port

                # 🔹 Try register
                if self.tcp_client.register_user(self.state.server, self.state):
                    self.udp_client.start_listener(self.state)
                    return

    def reset_session(self, message=None):
        self.udp_client.stop_listener()
        server = self.state.server
        self.state = ClientState(
            server=server,
            rq="REGISTER",
            ip_address=self.local_ip,
            subjects=[],
        )
        if message:
            print(message)

    def logout_user(self):
        self.reset_session("Logged out.")
        self.authenticate_user()

    def change_server(self):
        self.udp_client.stop_listener()
        new_server = self.ask_user_server()
        self.state = ClientState(server=new_server, rq="REGISTER", ip_address=self.local_ip, subjects=[])
        print(f"Server changed to {self.state.server['name']}")
        self.print_server_summary()
        self.authenticate_user()

    def print_server_summary(self):
        summary_lines = [
            ("Server", self.state.server["name"] if self.state.server else "Not set"),
            ("Host", self.state.server["connect_host"] if self.state.server else "Not set"),
            ("TCP Port", str(self.state.server["tcp_port"]) if self.state.server else "Not set"),
            ("UDP Port", str(self.state.server["udp_port"]) if self.state.server else "Not set"),
        ]
        content_lines = [f"{label:<8}: {value}" for label, value in summary_lines]
        inner_width = max(len("Server Config"), *(len(line) for line in content_lines))
        border = "+" + "-" * (inner_width + 2) + "+"

        print(border)
        print(f"| {'Server Config':^{inner_width}} |")
        print(border)
        for line in content_lines:
            print(f"| {line:<{inner_width}} |")
        print(border)
    
    def print_state_summary(self):
        summary_lines = [
            ("Server", self.state.server["name"] if self.state.server else "Not set"),
            ("User", self.state.name or "Not set"),
            ("IP", self.state.ip_address or "Not set"),
            ("TCP", str(self.state.tcp_port) if self.state.tcp_port is not None else "Not set"),
            ("UDP", str(self.state.udp_port) if self.state.udp_port is not None else "Not set"),
            ("Subjects", ", ".join(self.state.subjects or []) or "Not set"),
        ]
        content_lines = [f"{label:<8}: {value}" for label, value in summary_lines]
        inner_width = max(len("Client State"), *(len(line) for line in content_lines))
        border = "+" + "-" * (inner_width + 2) + "+"

        print(border)
        print(f"| {'Client State':^{inner_width}} |")
        print(border)
        for line in content_lines:
            print(f"| {line:<{inner_width}} |")
        print(border)
        
        
    def handle_command(self):
        print("\n")
        self.print_state_summary()
        print("Commands:")
        print("/register   Register the current user on this server.")
        print("/update     Update this user's IP address and ports.")
        print("/subjects   Update this user's subjects of interest.")
        print("/deregister Remove this user from the current server.")
        print("/logout     Clear the current session and authenticate again.")
        print("/server     Switch to another server and authenticate there.")
        print("/publish    Publish news over UDP.")
        print("/comment    Comment on a received news message over UDP.")
        command = input(">> ").lower().strip()
        command = command[1:] if command.startswith("/") else command

        if command == "register":
            self.state.ip_address = self.ask_user_ip_address(default=self.state.ip_address)
            self.tcp_client.register_user(self.state.server, self.state)

        elif command == "update":
            previous_ip = self.state.ip_address
            previous_tcp = self.state.tcp_port
            previous_udp = self.state.udp_port

            new_ip = self.ask_user_ip_address(default=self.state.ip_address)
            new_tcp = self.ask_user_tcp_port(current_port=self.state.tcp_port)
            new_udp = self.ask_user_udp_port(current_port=self.state.udp_port)

            self.state.ip_address = new_ip
            self.state.tcp_port = new_tcp
            self.state.udp_port = new_udp

            update_info = self.tcp_client.update_user(self.state.server, self.state)
            if update_info is not None:
                self.state.name = update_info["name"]
                self.state.ip_address = update_info["ip_address"]
                self.state.tcp_port = update_info["tcp_port"]
                self.state.udp_port = update_info["udp_port"]
                self.state.subjects = update_info["subjects"]
                self.udp_client.start_listener(self.state)
            else:
                self.state.ip_address = previous_ip
                self.state.tcp_port = previous_tcp
                self.state.udp_port = previous_udp

        elif command == "subjects":
            previous_subjects = list(self.state.subjects or [])
            self.state.subjects = self.ask_user_subjects()
            subjects_info = self.tcp_client.update_subjects(self.state.server, self.state)
            if subjects_info is not None:
                self.state.name = subjects_info["name"]
                self.state.subjects = subjects_info["subjects"]
            else:
                self.state.subjects = previous_subjects



        elif command == "deregister":
            if self.tcp_client.deregister_user(self.state.server, self.state):
                self.udp_client.stop_listener()
                server = self.state.server
                self.state = ClientState(
                    server=server,
                    rq="REGISTER",
                    ip_address=self.local_ip,
                    subjects=[],
                )
                print("User deregistered. Please login or register again.")
                self.authenticate_user()

        elif command == "publish":
            subject = self.ask_publish_subject()
            title = input("Enter title: ").strip()
            text = input("Enter text: ").strip()
            self.udp_client.publish_news(self.state.server, self.state, subject, title, text)

        elif command == "comment":
            subject = self.ask_publish_subject()
            title = input("Enter original message title: ").strip()
            text = input("Enter comment: ").strip()
            self.udp_client.publish_comment(self.state.server, self.state, subject, title, text)

        elif command == "logout":
            self.logout_user()
        elif command == "server":
            self.change_server()
        else:
            self.tcp_client.send_message(self.state.server, command)
        return command

    @staticmethod
    def ask_user_tcp_port(current_port=None):
        prompt = "Enter your tcp address"
        if current_port:
            prompt += f" [{current_port}]"
        prompt += ": "
        value = input(prompt).strip()
        return value or current_port

    @staticmethod
    def ask_user_udp_port(current_port=None):
        prompt = "Enter your udp address"
        if current_port:
            prompt += f" [{current_port}]"
        prompt += ": "
        value = input(prompt).strip()
        return value or current_port
            
    @staticmethod
    def ask_user_name():
        return input("Enter your name: ")

    @staticmethod
    def ask_user_ip_address(default=None):
        prompt = "Enter your IP address"
        if default:
            prompt += f" [{default}]"
        prompt += ": "
        value = input(prompt).strip()
        return value or default

    @staticmethod
    def ask_user_subjects():
        print(f"Available subjects: {', '.join(ALLOWED_SUBJECTS)}")
        raw_subjects = input("Enter subjects separated by commas: ").strip().lower()
        return [subject.strip() for subject in raw_subjects.split(",") if subject.strip()]

    @staticmethod
    def ask_publish_subject():
        return input("Enter publish subject: ").strip().lower()

    @staticmethod
    def ask_user_server():
        while True:
            server_name = input("Enter the server to connect to, [A or B]: ").strip().lower()
            if server_name == "a":
                server = dict(SERVER_A)
                server["connect_host"] = input("Enter Server A IP address: ").strip()
                return server
            if server_name == "b":
                server = dict(SERVER_B)
                server["connect_host"] = input("Enter Server B IP address: ").strip()
                return server