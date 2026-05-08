from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Diagnostic:
    severity: str  # 'error', 'warning', 'info'
    code: str  # e.g., 'SYL_ERR_UNDEFINED_COURSE'
    message: str
    line: int
    column: int
    hint: Optional[str] = None


class DiagnosticsCollector:
    def __init__(self):
        self.diagnostics: List[Diagnostic] = []

    def has_errors(self) -> bool:
        return any(d.severity == "ERROR" for d in self.diagnostics)

    def add_error(
        self, code: str, message: str, line: int, col: int, hint: str
    ) -> None:
        self.diagnostics.append(Diagnostic("ERROR", code, message, line, col, hint))

    def add_warning(
        self,
        code: str,
        message: str,
        line: int,
        col: int,
        hint: Optional[str] = None,
    ) -> None:
        self.diagnostics.append(Diagnostic("WARNING", code, message, line, col, hint))

    def report(self) -> None:
        """Prints formatted, educational diagnostics to the console."""
        for d in self.diagnostics:
            color = (
                "\033[91m"
                if d.severity == "ERROR"
                else "\033[93m" if d.severity == "WARNING" else "\033[94m"
            )
            reset = "\033[0m"
            print(
                f"{color}{d.severity} [{d.code}] at Line {d.line}, Column {d.column}: {d.message}{reset}"
            )
            if d.hint:
                print(f"  Hint: {d.hint}")
