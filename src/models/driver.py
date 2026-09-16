from dataclasses import dataclass
from typing import List, Optional
from .states import DriverState


@dataclass
class DriverInfo:
    name: str
    version: Optional[str]
    module_name: str
    state: DriverState
    loaded: bool
    interfaces: List[str]
