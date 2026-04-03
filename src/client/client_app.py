from src.client.state import ClientState
from src.client.tcp_client import TcpClient
from src.shared.config import ALLOWED_SUBJECTS, SERVER_A, SERVER_B


class ClientApp:
    def __init__(self, name=None, server=None):
        self.state = ClientState(
            name=name,
            server=server or SERVER_A,
            rq="REGISTER",
            ip_address="127.0.0.1",
            subjects=[],
        )
        self.tcp_client = TcpClient()

    def run(self):
        print("___Client has started___")

        # Set the user's name
        if self.state.name is None:
            # self.state.name = self.ask_user_name()
            # print(f"Name set to {self.state.name}")
            self.authenticate_user()
        else:
            login_info = self.tcp_client.login_user(self.state.server, self.state.name)
            if login_info is None:
                print(f"Failed to login, please authenticate yourself")
                self.authenticate_user()
            else:
                self.state.name = login_info["name"]
                self.state.ip_address = login_info["ip_address"]
                self.state.tcp_port = login_info["tcp_port"]
                self.state.udp_port = login_info["udp_port"]
                self.state.subjects = login_info["subjects"]
                
        print(f"Hi, {self.state.name}!")

        # Set server to connect to
        if self.state.server is None:
            self.state.server = self.ask_user_server()

        print(f"Server set to {self.state.server['name']}")
        
        # self.tcp_client.register_user(self.state.server, self.state)
        
        # Register with the server
        while True:
            self.handle_command()
    
    def authenticate_user(self):
        while True:
            print("Hi, please authenticate yourself:")
            print(f"commands: /login  /register")
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
                return

            if command == "register":
                self.state.name = self.ask_user_name()
                # self.state.ip_address = self.ask_user_ip_address(default=self.state.ip_address)
                self.state.tcp_port = self.ask_user_tcp_port()
                self.state.udp_port = self.ask_user_udp_port()
            
                if self.tcp_client.register_user(self.state.server, self.state):
                    return

    def logout_user(self):
        server = self.state.server
        self.state = ClientState(server=server, rq="REGISTER", ip_address="127.0.0.1", subjects=[])
        print("Logged out.")
        self.authenticate_user()

    def change_server(self):
        new_server = self.ask_user_server()
        self.state = ClientState(server=new_server, rq="REGISTER", ip_address="127.0.0.1", subjects=[])
        print(f"Server changed to {self.state.server['name']}")
        self.authenticate_user()
    
    def print_state_summary(self):
        summary_lines = [
            ("Server", self.state.server["name"] if self.state.server else "Not set"),
            ("User", self.state.name or "Not set"),
            ("IP", self.state.ip_address or "Not set"),
            ("TCP", str(self.state.tcp_port) if self.state.tcp_port is not None else "Not set"),
            ("UDP", str(self.state.udp_port) if self.state.udp_port is not None else "Not set"),
            ("Subjects", ", ".join(self.state.subjects or []) or "Not set"),
        ]
        endpoint = (
            f"{self.state.ip_address}:{self.state.tcp_port} (TCP) | "
            f"{self.state.ip_address}:{self.state.udp_port} (UDP)"
            if self.state.ip_address is not None
            and self.state.tcp_port is not None
            and self.state.udp_port is not None
            else "Not available"
        )
        content_lines = [f"{label:<8}: {value}" for label, value in summary_lines]
        # content_lines.append(f"Endpoint: {endpoint}")
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
        command = input(">> ").lower().strip()
        command = command[1:] if command.startswith("/") else command
        if command == "register":
            self.tcp_client.register_user(self.state.server, self.state)
        elif command == "update":
            # self.state.ip_address = self.ask_user_ip_address(default=self.state.ip_address)
            self.state.tcp_port = self.ask_user_tcp_port()
            self.state.udp_port = self.ask_user_udp_port()
            update_info = self.tcp_client.update_user(self.state.server, self.state)
            if update_info is not None:
                self.state.name = update_info["name"]
                self.state.ip_address = update_info["ip_address"]
                self.state.tcp_port = update_info["tcp_port"]
                self.state.udp_port = update_info["udp_port"]
                self.state.subjects = update_info["subjects"]
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
            self.tcp_client.deregister_user(self.state.server, self.state)
        elif command == "logout":
            self.logout_user()
        elif command == "server":
            self.change_server()
        else:
            self.tcp_client.send_message(self.state.server, command)
        return command

    @staticmethod
    def ask_user_tcp_port():
        return input("Enter your tcp: ").strip()

    @staticmethod
    def ask_user_udp_port():
        return input("Enter your udp port: ").strip()
            
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
    def ask_user_server():
        while True:
            server_name = input("Enter the server to connect to, [A or B]: ").strip().lower()
            if server_name == "a":
                return SERVER_A
            if server_name == "b":
                return SERVER_B
            print("Invalid server, please enter A or B")


def main():
    client = ClientApp(name="Ben")
    client.run()


if __name__ == "__main__":
    main()
