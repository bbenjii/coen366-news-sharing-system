from src.server.tcp_server import TcpServer
from src.shared.config import SERVER_A, get_local_ip


class ServerApp:

    def __init__(self, server_config=SERVER_A, peer_server_connect_host=None):
        self.local_ip = get_local_ip()
        self.server_config = server_config
        self.server_config["connect_host"] = self.local_ip

        self.tcp_server = TcpServer(server_config)
        self.peer_server_connect_host = peer_server_connect_host

    def print_config_summary(self):
        summary_lines = [
            ("Server", self.server_config["name"]),
            ("Bind Host", self.server_config["bind_host"]),
            ("Connect Host", self.server_config["connect_host"]),
            ("TCP Port", str(self.server_config["tcp_port"])),
            ("UDP Port", str(self.server_config["udp_port"])),
            ("Peer Server IP", self.peer_server_connect_host or "Not set"),
        ]
        inner_width = max(len("Server Config"), *(len(f"{label:<14}: {value}") for label, value in summary_lines))
        border = "+" + "-" * (inner_width + 2) + "+"

        print(border)
        print(f"| {'Server Config':^{inner_width}} |")
        print(border)
        for label, value in summary_lines:
            line = f"{label:<14}: {value}"
            print(f"| {line:<{inner_width}} |")
        print(border)

    def initialize_server_context(self):
        print(f"Local IP: {self.local_ip}")
        if self.peer_server_connect_host is None:
            self.peer_server_connect_host = input(
                "Enter the other server's IP address: "
            ).strip()
        print("___Server has started___")

    def run(self):
        self.initialize_server_context()
        self.print_config_summary()
        self.tcp_server.run()


def main():
    peer_ip = "192.168.2.208"
    server = ServerApp(peer_server_connect_host=peer_ip)
    server.run()


if __name__ == "__main__":
    main()
