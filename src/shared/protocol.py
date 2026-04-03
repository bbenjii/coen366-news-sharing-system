from src.shared import DeregisterModel, RegisterModel

def serialize_register(request: RegisterModel):
    return (
        f"REGISTER {request.rq} {request.name} {request.ip_address} {request.tcp_port} {request.udp_port}"
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


def serialize_registered(rq):
    return (
        f"REGISTERED {rq}"
    )

def parse_registered(message):
    parts = message.strip().split()
    return {
        "command": parts[0],
        "request_id": int(parts[1]),
    }

def serialize_register_denied(rq, reason):
    return (
        f"REGISTER-DENIED {rq} {reason}"
    )

def parse_register_denied(message):
    parts = message.strip().split()
    return {
        "command": parts[0],
        "request_id": int(parts[1]),
        "reason": parts[2],
    }


def serialize_deregister(request: DeregisterModel):
    return f"DE-REGISTER {request.rq} {request.name}"


def parse_deregister(message):
    parts = message.strip().split()
    return {
        "command": parts[0],
        "request_id": int(parts[1]),
        "name": parts[2],
    }
