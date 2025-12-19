from dataclasses import dataclass
from .materials import ReinforcedConcrete
import numpy as np


@dataclass
class RectangularSection:
    base: int
    height: int
    alpha: int = 1.5  # ABNT NBR 6118: 2014, art. 17.3, p. 17.3.1

    def area(self):
        return self.base * self.height

    def area_effective(self):
        return (self.base * self.height) / 1.5  # todo: test value

    def inertia(self):
        return (self.base * self.height**3) / 12


@dataclass
class ReinforcedConcreteSection:
    material: ReinforcedConcrete
    geometry: RectangularSection
    cover: int

    def d(self):
        return self.geometry.height - self.cover

    def alpha_e(self):
        return self.material.rebar.Es / self.material.concrete.ecs()

    def mcr(self):
        return (
            self.geometry.alpha
            * (self.material.concrete.fctm() / 10)
            * self.geometry.inertia()
        ) / (self.geometry.height / 2)

    def x1(self):
        return (
            ((self.geometry.base * self.geometry.height**2) / 2)
            + (self.alpha_e() - 1) * self.material.rebar.As * self.d()
        ) / (self.geometry.area() + (self.alpha_e() - 1) * self.material.rebar.As)

    def inertia1(self):
        return (
            self.geometry.inertia()
            + self.geometry.area() * (self.x1() - self.geometry.height / 2) ** 2
            + (self.alpha_e() - 1)
            * self.material.rebar.As
            * (self.d() - self.x1()) ** 2
        )

    def x2(self):
        a = self.geometry.base / 2
        b = (self.alpha_e() - 1) * self.material.rebar.As
        c = -(self.alpha_e() - 1) * self.material.rebar.As * self.d()
        coeff = [a, b, c]
        possible_values = np.roots(coeff)
        for val in possible_values:
            if 0 < val < self.geometry.height:
                return val
        return 0

    def inertia2(self):
        return (
            self.geometry.base * self.x2() ** 3
        ) / 3 + self.alpha_e() * self.material.rebar.As * (self.d() - self.x2()) ** 2

    def ea(self):
        return self.material.concrete.eci() * self.geometry.area()

    def ei1(self):
        return self.material.concrete.ecs() * self.inertia1()
