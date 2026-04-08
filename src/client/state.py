from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ClientState:
    name: str | None = None
    server: dict | None = None
    rq: str | None = None
    ip_address: str | None = None
    tcp_port: int | None = None
    udp_port: int | None = None
    subjects: list[str] | None = None
