from dataclasses import dataclass


@dataclass
class DistributedLoad:
    start: float
    end: float
    value: float  # kN/m (ou unidade consistente)
