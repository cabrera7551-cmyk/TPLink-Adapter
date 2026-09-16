from dataclasses import dataclass
from typing import Optional, List
from .states import ConnectionState


@dataclass
class ConnectionInfo:
    ssid: Optional[str]
    bssid: Optional[str]
    frequency: Optional[int]
    channel: Optional[int]
    signal: Optional[int]
    tx_bitrate: Optional[str]
    rx_bitrate: Optional[str]
    ip_address: Optional[str]
    gateway: Optional[str]
    dns: List[str]
    state: ConnectionState
