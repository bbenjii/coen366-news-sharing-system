from dataclasses import dataclass

@dataclass
class RegisterModel:
    rq: str
    name: str
    ip_address: str
    tcp_port: int
    udp_port: int

@dataclass
class ClientConfig:
    rq: str
    name: str
    ip_address: str
    tcp_port: int
    udp_port: int
    
    
@dataclass
class RegisteredModel:
    rq: str

@dataclass
class RegisterDeniedModel:
    rq: str
    reason: str


@dataclass
class DeregisterModel:
    rq: str
    name: str


@dataclass
class LoginModel:
    rq: str
    name: str


@dataclass
class LoginConfirmedModel:
    rq: str
    name: str
    ip_address: str
    tcp_port: int
    udp_port: int
    subjects: list[str]


@dataclass
class LoginDeniedModel:
    rq: str
    reason: str


@dataclass
class UpdateModel:
    rq: str
    name: str
    ip_address: str
    tcp_port: int
    udp_port: int


@dataclass
class UpdateConfirmedModel:
    rq: str
    name: str
    ip_address: str
    tcp_port: int
    udp_port: int
    subjects: list[str]


@dataclass
class UpdateDeniedModel:
    rq: str
    reason: str


@dataclass
class SubjectsModel:
    rq: str
    name: str
    subjects: list[str]


@dataclass
class SubjectsUpdatedModel:
    rq: str
    name: str
    subjects: list[str]


@dataclass
class SubjectsRejectedModel:
    rq: str
    name: str
    subjects: list[str]


@dataclass
class PublishModel:
    rq: str
    name: str
    subject: str
    title: str
    text: str


@dataclass
class PublishDeniedModel:
    rq: str
    reason: str


@dataclass
class MessageModel:
    name: str
    subject: str
    title: str
    text: str


@dataclass
class ForwardModel:
    name: str
    subject: str
    title: str
    text: str
