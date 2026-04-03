from src.client.state import ClientState
from src.client.tcp_client import TcpClient
from src.shared.config import SERVER_A, SERVER_B


class ClientApp:
    def __init__(self, name=None, server=None):
        self.state = ClientState(name=name, server=server or SERVER_A)
        self.tcp_client = TcpClient()

    def run(self):
        print("___Client has started___")

        # Set the user's name
        if self.state.name is None:
            self.state.name = self.ask_user_name()
            print(f"Name set to {self.state.name}")

        print(f"Hi, {self.state.name}!")

        # Set server to connect to
        if self.state.server is None:
            self.state.server = self.ask_user_server()

        print(f"Server set to {self.state.server['name']}")

        while True:
            self.handle_command()
    
    
    def handle_command(self):
        command = input("Enter a command: ")
        self.tcp_client.send_message(self.state.server, command)
        return command

    @staticmethod
    def ask_user_name():
        return input("Enter your name: ")

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
