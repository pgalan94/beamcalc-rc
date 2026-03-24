from dataclasses import dataclass


@dataclass
class Support:
    position: float
    type: str  # "hinged", "fixed", "roller"
