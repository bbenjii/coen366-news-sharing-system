SEPARATOR = "|"


def parse_message(raw_message: str) -> dict:
    raw_message = raw_message.strip()
    parts = raw_message.split(SEPARATOR)

    return {
        "command": parts[0],
        "fields": parts[1:],
    }


def _join_parts(*parts) -> str:
    return SEPARATOR.join(str(part) for part in parts)


def build_register(rq_id: str, name: str, ip_address: str, tcp_port: int, udp_port: int) -> str:
    return _join_parts("REGISTER", rq_id, name, ip_address, tcp_port, udp_port)


def build_registered(rq_id: str) -> str:
    return _join_parts("REGISTERED", rq_id)


def build_register_denied(rq_id: str, reason: str) -> str:
    return _join_parts("REGISTER-DENIED", rq_id, reason)


def build_refer(rq_id: str, other_server_ip: str) -> str:
    return _join_parts("REFER", rq_id, other_server_ip)


def build_deregister(rq_id: str, name: str) -> str:
    return _join_parts("DE-REGISTER", rq_id, name)


def build_deregistered(rq_id: str) -> str:
    return _join_parts("DE-REGISTERED", rq_id)


def build_deregister_denied(rq_id: str, reason: str) -> str:
    return _join_parts("DE-REGISTER-DENIED", rq_id, reason)


def build_update(rq_id: str, name: str, ip_address: str, tcp_port: int, udp_port: int) -> str:
    return _join_parts("UPDATE", rq_id, name, ip_address, tcp_port, udp_port)


def build_update_confirmed(
    rq_id: str,
    name: str,
    ip_address: str,
    tcp_port: int,
    udp_port: int,
) -> str:
    return _join_parts("UPDATE-CONFIRMED", rq_id, name, ip_address, tcp_port, udp_port)


def build_update_denied(rq_id: str, reason: str) -> str:
    return _join_parts("UPDATE-DENIED", rq_id, reason)


def build_subjects(rq_id: str, name: str, subjects: str) -> str:
    return _join_parts("SUBJECTS", rq_id, name, subjects)


def build_subjects_updated(rq_id: str, name: str, subjects: str) -> str:
    return _join_parts("SUBJECTS-UPDATED", rq_id, name, subjects)


def build_subjects_rejected(rq_id: str, name: str, subjects: str, reason: str) -> str:
    return _join_parts("SUBJECTS-REJECTED", rq_id, name, subjects, reason)


def build_publish(rq_id: str, name: str, subject: str, title: str, text: str) -> str:
    return _join_parts("PUBLISH", rq_id, name, subject, title, text)


def build_publish_denied(rq_id: str, reason: str) -> str:
    return _join_parts("PUBLISH-DENIED", rq_id, reason)


def build_message(name: str, subject: str, title: str, text: str) -> str:
    return _join_parts("MESSAGE", name, subject, title, text)


def build_publish_comment(name: str, subject: str, title: str, text: str) -> str:
    return _join_parts("PUBLISH-COMMENT", name, subject, title, text)


def build_comment(name: str, subject: str, title: str, text: str) -> str:
    return _join_parts("COMMENT", name, subject, title, text)


def build_comment_denied(reason: str) -> str:
    return _join_parts("COMMENT-DENIED", reason)


def build_forward(name: str, subject: str, title: str, text: str) -> str:
    return _join_parts("FORWARD", name, subject, title, text)


def build_forward_comment(name: str, subject: str, title: str, text: str) -> str:
    return _join_parts("FORWARD-COMMENT", name, subject, title, text)