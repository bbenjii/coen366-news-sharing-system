from src.shared import RegisterModel

def serialize_register(request: RegisterModel):
    return (
        f"REGISTER {request.rq} {request.name} "
        f"{request.ip_address} {request.tcp_port} {request.udp_port}"
    )


def parse_register(message):
    parts = message.strip().split()
    return {
        "command": parts[0],
        "request_id": int(parts[1]),
        "name": parts[2],
        "ip_address": parts[3],
        "tcp_port": int(parts[4]),
        "udp_port": int(parts[5]),
    }