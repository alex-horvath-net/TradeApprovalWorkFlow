from dataclasses import dataclass

@dataclass(frozen=True)
class TradeDiff:
    changes: dict[str, tuple[str, str]]
