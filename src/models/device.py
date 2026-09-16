from dataclasses import dataclass, field
from typing import Optional
from .states import DeviceState


@dataclass
class USBDevice:
    vendor_id: str
    product_id: str
    vendor_name: str
    product_name: str
    device_path: str
    chipset: Optional[str] = None
    state: DeviceState = DeviceState.DETECTED
