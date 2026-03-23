from dataclasses import dataclass
from math import exp


@dataclass
class Rebar:
    fyk: int
    ys: float
    gamma: int
    Es: int
    As: int
    As_neg: int


@dataclass
class Concrete:
    fck: int
    yc: float
    gamma: int
    CP: int
    v: float = 0.20
    alpha: float = 0.00001

    def fcd(self):
        return self.fckj() / self.yc

    def fctm(self):
        return 0.3 * self.fckj() ** (2 / 3)

    def fctk_inf(self):
        return 0.7 * self.fctm()

    def fctk_sup(self):
        return 1, 3 * self.fctm()

    def eci(self):
        return 5600 * (self.fckj() ** (1 / 2))

    def ecs(self):
        return (0.8 + 0.2 * (self.fckj() / 80)) * self.ecij()

    def gc(self):
        return 0.4 * self.ecs()

    def fckj(self, days=28):
        """
        s = 0,38 para concreto de cimento CPIII e CPIV;
        s = 0,25 para concreto de cimento CPI e CPII
        s = 0,20 para concreto de cimento CPV-ARI; fonte NBR 6118:2014
        :param days: int
        :return: int
        """
        if self.CP < 1 or self.CP > 5:
            return -1
        elif self.CP < 3:
            s = 0.25
        elif self.CP < 5:
            s = 0.38
        else:
            s = 0.20
        betta = exp(s * (1 - (28 / days) ** 0.5))
        fckj = betta * self.fck
        return fckj

    def fcdj(self, j=28):
        return self.fckj(j) / self.yc

    def ecij(self, days=28):
        return 5600 * (self.fckj(days) ** (1 / 2))


@dataclass
class ReinforcedConcrete:
    concrete: Concrete
    rebar: Rebar
