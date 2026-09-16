from dataclasses import dataclass
from typing import Optional, List, Dict


@dataclass
class PhyInfo:
    name: str
    interface_name: str
    modes: List[str]
    bands: Dict[str, List[int]]
    current_mode: Optional[str] = None
