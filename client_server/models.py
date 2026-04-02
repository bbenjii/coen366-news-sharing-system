from dataclasses import dataclass, field
from typing import List


@dataclass
class User:
    name: str
    ip_address: str
    tcp_port: int
    udp_port: int
    subjects: list[str] = field(default_factory=list)


@dataclass
class NewsMessage:
    sender: str
    subject: str
    title: str
    text: str


@dataclass
class Comment:
    sender: str
    subject: str
    title: str
    text: str