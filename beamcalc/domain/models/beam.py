from dataclasses import dataclass, field
from typing import List


@dataclass
class Beam:
    length: float
    section: object = None
    supports: List[object] = field(default_factory=list)
    loads: List[object] = field(default_factory=list)

    def set_section(self, section):
        self.section = section

    def add_support(self, support):
        self.supports.append(support)

    def add_load(self, load):
        self.loads.append(load)

    def validate(self):
        if self.length <= 0:
            raise ValueError("Beam length must be greater than zero")

        if self.section is None:
            raise ValueError("Beam must have a section")

        if len(self.supports) == 0:
            raise ValueError("Beam must have at least one support")
