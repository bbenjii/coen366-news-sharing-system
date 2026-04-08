from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ClientState:
    name: Optional[str] = None
    server: Optional[Dict[str, Any]] = None
    rq: Optional[str] = None
    ip_address: Optional[str] = None
    tcp_port: Optional[int] = None
    udp_port: Optional[int] = None
    subjects: Optional[List[str]] = None
