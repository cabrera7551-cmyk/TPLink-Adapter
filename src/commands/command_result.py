from dataclasses import dataclass
from typing import Optional
from .states import CommandResultState


@dataclass
class CommandResult:
    state: CommandResultState
    output: str = ""
    error: Optional[str] = None
    returncode: int = 0
    command: Optional[str] = None

    @property
    def success(self) -> bool:
        return self.state == CommandResultState.SUCCESS

    @property
    def failed(self) -> bool:
        return self.state != CommandResultState.SUCCESS
