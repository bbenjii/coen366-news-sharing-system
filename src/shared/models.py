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


