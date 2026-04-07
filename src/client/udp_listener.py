import socket
import threading

class UdpListener:
    def __init__(self, ip, port):
        self.address = (ip, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def start(self):
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()

    def run(self):
        self.socket.bind(self.address)
        print(f"[UDP CLIENT] Listening on {self.address}")

        while True:
            data, addr = self.socket.recvfrom(4096)
            print(f"[UDP CLIENT] Received: {data.decode()}")