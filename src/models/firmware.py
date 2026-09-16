from dataclasses import dataclass
from typing import List, Optional
from .states import FirmwareState


@dataclass
class FirmwareInfo:
    version: Optional[str]
    state: FirmwareState
    errors: List[str]
    load_errors: List[str]
