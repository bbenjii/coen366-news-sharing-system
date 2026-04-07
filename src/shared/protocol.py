from src.shared import (
    ALLOWED_SUBJECTS,
    DeregisterModel,
    LoginConfirmedModel,
    LoginDeniedModel,
    LoginModel,
    RegisterModel,
    SubjectsModel,
    SubjectsRejectedModel,
    SubjectsUpdatedModel,
    UpdateConfirmedModel,
    UpdateDeniedModel,
    UpdateModel,
)
import ipaddress


def _serialize_subjects(subjects: list[str]):
    return ",".join(subjects)


def _parse_subjects(encoded_subjects: str):
    if not encoded_subjects:
        return []
    return [subject for subject in encoded_subjects.split(",") if subject]


def _parse_port(value: str):
    try:
        return int(value)
    except ValueError:
        return None

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
        "tcp_port": _parse_port(parts[4]),
        "udp_port": _parse_port(parts[5]),
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
        f"{response.ip_address} {response.tcp_port} {response.udp_port} "
        f"{_serialize_subjects(response.subjects)}"
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
        "subjects": _parse_subjects(parts[6] if len(parts) > 6 else ""),
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
        "tcp_port": _parse_port(parts[4]),
        "udp_port": _parse_port(parts[5]),
    }


def serialize_update_confirmed(response: UpdateConfirmedModel):
    return (
        f"UPDATE-CONFIRMED {response.rq} {response.name} "
        f"{response.ip_address} {response.tcp_port} {response.udp_port} "
        f"{_serialize_subjects(response.subjects)}"
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
        "subjects": _parse_subjects(parts[6] if len(parts) > 6 else ""),
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


def serialize_subjects(request: SubjectsModel):
    return (
        f"SUBJECTS {request.rq} {request.name} "
        f"{_serialize_subjects(request.subjects)}"
    )


def parse_subjects(message):
    parts = message.strip().split()
    return {
        "command": parts[0],
        "request_id": int(parts[1]),
        "name": parts[2],
        "subjects": _parse_subjects(parts[3] if len(parts) > 3 else ""),
    }


def serialize_subjects_updated(response: SubjectsUpdatedModel):
    return (
        f"SUBJECTS-UPDATED {response.rq} {response.name} "
        f"{_serialize_subjects(response.subjects)}"
    )


def parse_subjects_updated(message):
    parts = message.strip().split()
    return {
        "command": parts[0],
        "request_id": int(parts[1]),
        "name": parts[2],
        "subjects": _parse_subjects(parts[3] if len(parts) > 3 else ""),
    }


def serialize_subjects_rejected(response: SubjectsRejectedModel):
    return (
        f"SUBJECTS-REJECTED {response.rq} {response.name} "
        f"{_serialize_subjects(response.subjects)}"
    )


def parse_subjects_rejected(message):
    parts = message.strip().split()
    return {
        "command": parts[0],
        "request_id": int(parts[1]),
        "name": parts[2],
        "subjects": _parse_subjects(parts[3] if len(parts) > 3 else ""),
    }


def is_valid_ip_address(value: str):
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def is_valid_port(value):
    return isinstance(value, int) and 1 <= value <= 65535

def parse_publish(message):
    parts = message.strip().split(maxsplit=5)

    if len(parts) < 6:
        return None

    return {
        "command": parts[0],
        "request_id": parts[1],
        "name": parts[2],
        "subject": parts[3],
        "title": parts[4],
        "text": parts[5],
    }

def serialize_message(name, subject, title, text):
    return f"MESSAGE {name} {subject} {title} {text}"

def parse_publish_comment(message):
    parts = message.strip().split(maxsplit=4)
    return {
        "command": parts[0],
        "name": parts[1],
        "subject": parts[2],
        "title": parts[3],
        "text": parts[4],
    }


def serialize_comment(name, subject, title, text):
    return f"COMMENT {name} {subject} {title} {text}"

def serialize_publish_denied(rq, reason):
    return f"PUBLISH-DENIED {rq} {reason}"