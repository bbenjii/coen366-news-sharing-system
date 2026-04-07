import socket

bind_host = "localhost"

ALLOWED_SUBJECTS = [
    "ai",
    "networking",
    "security",
    "software",
    "systems",
    "sports",
    "chess",
    "health",
    "travel"
]

SERVER_A = {
    "name": "Server A",
    "bind_host": "0.0.0.0",
    "connect_host": "",
    "tcp_port": 10000,
    "udp_port": 20000,
}

SERVER_B = {
    "name": "Server B",
    "bind_host": "0.0.0.0",
    "connect_host":"",
    "tcp_port": 10001,
    "udp_port": 20001,
}

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()

