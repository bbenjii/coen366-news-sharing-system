import os

SERVER_NAME = os.getenv("SERVER_NAME", "ServerA")
SERVER_IP = os.getenv("SERVER_IP", "127.0.0.1")

TCP_PORT = int(os.getenv("TCP_PORT", "5050"))
UDP_PORT = int(os.getenv("UDP_PORT", "5051"))

OTHER_SERVER_NAME = os.getenv("OTHER_SERVER_NAME", "ServerB")
OTHER_SERVER_IP = os.getenv("OTHER_SERVER_IP", "127.0.0.1")
OTHER_SERVER_TCP_PORT = int(os.getenv("OTHER_SERVER_TCP_PORT", "5060"))
OTHER_SERVER_UDP_PORT = int(os.getenv("OTHER_SERVER_UDP_PORT", "5061"))

ALLOWED_SUBJECTS = [
    "sports",
    "news",
    "technology",
    "health",
    "finance",
]

SERVER_REGION_IPS = {
    "ServerA": {"127.0.0.1"},
    "ServerB": {"127.0.0.2"},
}

DATA_DIR = "data"
STATE_FILE = os.path.join(DATA_DIR, f"{SERVER_NAME.lower()}_state.json")
LOG_FILE = os.path.join(DATA_DIR, f"{SERVER_NAME.lower()}.log")


def ip_belongs_to_this_server(ip_address: str) -> bool:
    return ip_address in SERVER_REGION_IPS.get(SERVER_NAME, set())


def get_other_server_ip() -> str:
    return OTHER_SERVER_IP