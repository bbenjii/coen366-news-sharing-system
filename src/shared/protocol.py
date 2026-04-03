from src.shared import (
    DeregisterModel,
    LoginConfirmedModel,
    LoginDeniedModel,
    LoginModel,
    RegisterModel,
    UpdateConfirmedModel,
    UpdateDeniedModel,
    UpdateModel,
)

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


def serialize_login(request: LoginModel):
    return f"LOGIN {request.rq} {request.name}"


def parse_login(message):
    parts = message.strip().split()
    return {
        "command": parts[0],
        "request_id": int(parts[1]),
        "name": parts[2],
    }


def serialize_login_confirmed(response: LoginConfirmedModel):
    return (
        f"LOGIN-CONFIRMED {response.rq} {response.name} "
        f"{response.ip_address} {response.tcp_port} {response.udp_port}"
    )


def parse_login_confirmed(message):
    parts = message.strip().split()
    return {
        "command": parts[0],
        "request_id": int(parts[1]),
        "name": parts[2],
        "ip_address": parts[3],
        "tcp_port": int(parts[4]),
        "udp_port": int(parts[5]),
    }


def serialize_login_denied(response: LoginDeniedModel):
    return f"LOGIN-DENIED {response.rq} {response.reason}"


def parse_login_denied(message):
    parts = message.strip().split()
    return {
        "command": parts[0],
        "request_id": int(parts[1]),
        "reason": parts[2],
    }


def serialize_update(request: UpdateModel):
    return (
        f"UPDATE {request.rq} {request.name} "
        f"{request.ip_address} {request.tcp_port} {request.udp_port}"
    )


def parse_update(message):
    parts = message.strip().split()
    return {
        "command": parts[0],
        "request_id": int(parts[1]),
        "name": parts[2],
        "ip_address": parts[3],
        "tcp_port": int(parts[4]),
        "udp_port": int(parts[5]),
    }


def serialize_update_confirmed(response: UpdateConfirmedModel):
    return (
        f"UPDATE-CONFIRMED {response.rq} {response.name} "
        f"{response.ip_address} {response.tcp_port} {response.udp_port}"
    )


def parse_update_confirmed(message):
    parts = message.strip().split()
    return {
        "command": parts[0],
        "request_id": int(parts[1]),
        "name": parts[2],
        "ip_address": parts[3],
        "tcp_port": int(parts[4]),
        "udp_port": int(parts[5]),
    }


def serialize_update_denied(response: UpdateDeniedModel):
    return f"UPDATE-DENIED {response.rq} {response.reason}"


def parse_update_denied(message):
    parts = message.strip().split()
    return {
        "command": parts[0],
        "request_id": int(parts[1]),
        "reason": parts[2],
    }
