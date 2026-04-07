import socket

class UdpClient:
    def __init__(self, ip, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((ip, int(port)))  # same port for send + receive

    def publish(self, server, name, rq, subject, title, text):
        message = f"PUBLISH {rq} {name} {subject} {title} {text}"
        print(f"[UDP CLIENT] Sending: {message}")

        self.socket.sendto(
            message.encode(),
            (server["bind_host"], server["udp_port"])
        )

    def listen(self):
        while True:
            data, addr = self.socket.recvfrom(4096)
            print(f"[UDP CLIENT] Received: {data.decode()}")