from dataclasses import dataclass


@dataclass
class ClientState:
    name: str | None = None
    server: dict | None = None
