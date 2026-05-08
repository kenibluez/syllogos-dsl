import json
from dataclasses import dataclass, asdict
from typing import List, Optional


@dataclass
class Diagnostic:
    severity: str  # 'ERROR', 'WARNING', 'INFO'
    code: str  # Stable ID: e.g., 'SYL_ERR_UNDEFINED_COURSE'
    message: str
    line: int
    column: int
    hint: Optional[str] = None


class DiagnosticsCollector:
    def __init__(self):
        self.diagnostics: List[Diagnostic] = []

    def add_error(
        self, code: str, message: str, line: int, column: int, hint: str = None
    ):
        self.diagnostics.append(Diagnostic("ERROR", code, message, line, column, hint))

    def add_warning(
        self, code: str, message: str, line: int, column: int, hint: str = None
    ):
        self.diagnostics.append(
            Diagnostic("WARNING", code, message, line, column, hint)
        )

    def has_errors(self) -> bool:
        return any(d.severity == "ERROR" for d in self.diagnostics)

    def sort(self):
        """Sorts diagnostics deterministically by line, then column. Crucial for snapshot testing."""
        self.diagnostics.sort(key=lambda d: (d.line, d.column, d.code))

    def to_json(self) -> str:
        """Exports diagnostics for IDE Language Servers or UI consumption."""
        self.sort()
        return json.dumps([asdict(d) for d in self.diagnostics], indent=2)

    def report(self):
        """CLI-friendly educational output."""
        self.sort()
        for d in self.diagnostics:
            color = "\033[91m" if d.severity == "ERROR" else "\033[93m"
            reset = "\033[0m"
            print(
                f"{color}{d.severity} [{d.code}] Line {d.line}, Col {d.column}{reset}"
            )
            print(f"  {d.message}")
            if d.hint:
                print(f"  Hint: {d.hint}\n")
