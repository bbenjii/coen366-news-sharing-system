import socket


from src.utils.logger import get_logger

# bind_host = "127.0.0.1"
bind_host = "localhost"

SERVER_A = {
    "name": "Server A",
    "bind_host": bind_host,
    "tcp_port": 10000,
    "udp_port": 20000,
}

SERVER_B = {
    "name": "Server B",
    "bind_host": bind_host,
    "tcp_port": 10001,
    "udp_port": 20001,
}

logger = get_logger(__name__)

class Client:
    def __init__(self):
        self.name = "Ben"
        self.server = SERVER_A

        
    def run(self):
        print(f"___Client has started___")
        
        # Set a name if not set
        if self.name is None:
            self.name = self.ask_user_name()
            print(f"Name set to {self.name}")
        
        print(f"Hi, {self.name}!")

        # Select a server to connect to
        if self.server is None:
            self.server = self.ask_user_server()
        print(f"Server set to {self.server['name']}")

        while True:
            self.handle_command()
    @staticmethod
    def handle_command():
        command = input("Enter a command: ")
        return command
    
    @staticmethod
    def ask_user_name():
        name = input("Enter your name: ")
        return name
    
    @staticmethod
    def ask_user_server():
        valid = False
        server = None
        while not valid:
            server = input("Enter the server to connect to, [A or B]: ")
            if server.strip().lower() not in ["a", "b"]:
                print("Invalid server, please enter A or B")
                continue
            
            if server.strip().lower() == "a":
                server = SERVER_A
                valid = True
            else:
                server = SERVER_B
                valid = True
                
        return server
    
def main():
    client = Client()
    client.run()

if __name__ == '__main__':
    main()