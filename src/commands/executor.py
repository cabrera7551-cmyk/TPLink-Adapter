import subprocess
import shutil
from typing import Optional
from .command_result import CommandResult
from .states import CommandResultState
from .system_commands import SystemCommand


class CommandExecutor:
    """Safe command execution with error handling and timeouts."""

    def __init__(self):
        self._sudo_available = self._check_sudo_available()

    def _check_sudo_available(self) -> bool:
        """Check if sudo is available."""
        try:
            result = subprocess.run(
                ["sudo", "-n", "true"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def command_exists(self, command: str) -> bool:
        """Check if a command exists in the system."""
        return shutil.which(command) is not None

    def has_sudo(self) -> bool:
        """Check if sudo is available."""
        return self._sudo_available

    def execute(
        self,
        command: str,
        timeout: int = 30,
        require_sudo: bool = False
    ) -> CommandResult:
        """
        Execute a command safely with error handling.

        Args:
            command: Command string to execute
            timeout: Timeout in seconds
            require_sudo: Whether command requires sudo

        Returns:
            CommandResult with structured outcome
        """
        # Check if command exists
        cmd_name = command.split()[0]
        if not self.command_exists(cmd_name):
            return CommandResult(
                state=CommandResultState.COMMAND_NOT_FOUND,
                error=f"Command not found: {cmd_name}",
                command=command
            )

        # Check sudo if required
        if require_sudo and not self.has_sudo():
            return CommandResult(
                state=CommandResultState.PERMISSION_DENIED,
                error="Insufficient permissions (sudo required)",
                command=command
            )

        # Add sudo if required
        if require_sudo:
            command = f"sudo {command}"

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            # Check return code
            if result.returncode != 0:
                state = self._classify_error(result.stderr, result.returncode)
                return CommandResult(
                    state=state,
                    output=result.stdout,
                    error=result.stderr,
                    returncode=result.returncode,
                    command=command
                )

            # Check for empty output
            if not result.stdout.strip():
                return CommandResult(
                    state=CommandResultState.EMPTY_OUTPUT,
                    output="",
                    command=command
                )

            return CommandResult(
                state=CommandResultState.SUCCESS,
                output=result.stdout,
                returncode=result.returncode,
                command=command
            )

        except subprocess.TimeoutExpired:
            return CommandResult(
                state=CommandResultState.TIMEOUT,
                error="Command timeout",
                command=command
            )
        except PermissionError:
            return CommandResult(
                state=CommandResultState.PERMISSION_DENIED,
                error="Permission denied",
                command=command
            )
        except FileNotFoundError:
            return CommandResult(
                state=CommandResultState.COMMAND_NOT_FOUND,
                error="Command not found",
                command=command
            )
        except Exception as e:
            return CommandResult(
                state=CommandResultState.ERROR,
                error=str(e),
                command=command
            )

    def _classify_error(self, stderr: str, returncode: int) -> CommandResultState:
        """Classify error based on stderr and return code."""
        stderr_lower = stderr.lower()

        if "no such device" in stderr_lower or "cannot find device" in stderr_lower:
            return CommandResultState.NO_SUCH_DEVICE
        if "permission denied" in stderr_lower or "operation not permitted" in stderr_lower:
            return CommandResultState.PERMISSION_DENIED
        if "operation not supported" in stderr_lower or "unavailable" in stderr_lower:
            return CommandResultState.UNAVAILABLE

        return CommandResultState.NONZERO_EXIT

    def execute_system_command(
        self,
        system_command: SystemCommand,
        *args,
        timeout: Optional[int] = None
    ) -> CommandResult:
        """
        Execute a predefined SystemCommand with arguments.

        Args:
            system_command: SystemCommand to execute
            *args: Arguments to format into the command
            timeout: Override default timeout

        Returns:
            CommandResult with structured outcome
        """
        command = system_command.command.format(*args)
        timeout = timeout or system_command.timeout
        return self.execute(command, timeout=timeout, require_sudo=system_command.requires_sudo)
