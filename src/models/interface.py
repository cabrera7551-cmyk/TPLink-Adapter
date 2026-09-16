from dataclasses import dataclass
from typing import Optional, List
from .states import InterfaceState


@dataclass
class NetworkInterface:
    name: str
    mac_address: str
    state: InterfaceState
    ip_address: Optional[str] = None
    phy_name: Optional[str] = None
    device_path: Optional[str] = None
    nm_managed: bool = False
    rfkill_blocked: bool = False
