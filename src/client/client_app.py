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
                self.state.tcp_port = self.ask_user_tcp_port()
                self.state.udp_port = self.ask_user_udp_port()
            
                if self.tcp_client.register_user(self.state.server, self.state):
                    return

    def logout_user(self):
        server = self.state.server
        self.state = ClientState(server=server, rq="REGISTER", ip_address="127.0.0.1", subjects=[])
        print("Logged out.")
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
        print(f"commands: /register  /update  /subjects  /deregister  /logout")
        command = input(">> ").lower().strip()
        command = command[1:] if command.startswith("/") else command
        if command == "register":
            self.tcp_client.register_user(self.state.server, self.state)
        elif command == "update":
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
        else:
            self.tcp_client.send_message(self.state.server, command)
        return command

    @staticmethod
    def ask_user_tcp_port():
        while True:
            try:
                port = int(input("Enter your tcp: "))
                if 0 <= port <= 65535:
                    return port
            except ValueError:
                pass  # Fall through to the error message below

            print("Invalid port, please enter an integer between 0 and 65535.")

    @staticmethod
    def ask_user_udp_port():
        while True:
            try:
                port = int(input("Enter your udp port: "))
                if 0 <= port <= 65535:
                    return port
            except ValueError:
                pass  # Fall through to the error message below

            print("Invalid port, please enter an integer between 0 and 65535.")
            
    @staticmethod
    def ask_user_name():
        return input("Enter your name: ")

    @staticmethod
    def ask_user_subjects():
        print(f"Available subjects: {', '.join(ALLOWED_SUBJECTS)}")
        while True:
            raw_subjects = input("Enter subjects separated by commas: ").strip().lower()
            subjects = [subject.strip() for subject in raw_subjects.split(",") if subject.strip()]
            if subjects and all(subject in ALLOWED_SUBJECTS for subject in subjects):
                return subjects
            print("Invalid subjects, please choose from the available list.")

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
