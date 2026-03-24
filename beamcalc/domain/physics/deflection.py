from dataclasses import dataclass


@dataclass
class SectionProperties:
    inertia_uncracked: float  # I1
    inertia_cracked: float  # I2
    mr: float  # momento de fissuração
    ecs: float  # módulo do concreto


class BransonModel:
    def __init__(self, n: int = 3):
        self.n = n

    def effective_inertia(self, props: SectionProperties, ma: float) -> float:
        mr = props.mr
        i1 = props.inertia_uncracked
        i2 = props.inertia_cracked

        if ma == 0:
            return i1

        ratio = min(abs(mr / ma), 1.0)

        return (ratio**self.n) * i1 + (1 - ratio**self.n) * i2


class BischoffModel:
    def effective_inertia(self, props: SectionProperties, ma: float) -> float:
        mr = props.mr
        i1 = props.inertia_uncracked
        i2 = props.inertia_cracked

        if ma == 0:
            return i1

        ratio = min(abs(mr / ma), 1.0)

        return i2 / (1 - (ratio**2) * (1 - (i2 / i1)))


class DeflectionCalculator:
    def __init__(self, inertia_model):
        self.inertia_model = inertia_model

    def calculate(self, length: float, props: SectionProperties, ma: float):
        ie = self.inertia_model.effective_inertia(props, ma)

        return (5 * ma * length**2) / (48 * (props.ecs / 10) * ie)
