from dataclasses import dataclass, field
from typing import Dict, List
import numpy as np
from math import exp


@dataclass
class NodeObject:
    id: int
    V: float
    M: float
    uy: float
    phi: float


@dataclass
class BarObject:
    id: int
    EI: float
    EA: float
    cracked: bool
    nodes: Dict[int, NodeObject]


@dataclass
class LoadCaseObject:
    load: float
    bars: Dict[int, BarObject]
    branson: float
    bischoff: float

    def get_max_moment(self):
        return max(
            [abs(n.M) for b in self.bars.values() for n in b.nodes.values()] or [0]
        )

    def get_max_deflection(self):
        return max(
            [abs(n.uy) for b in self.bars.values() for n in b.nodes.values()] or [0]
        )


@dataclass
class BeamAnalysis:
    name: str
    cases: Dict[float, LoadCaseObject] = field(default_factory=dict)


# --- REGRAS DE NEGÓCIO E EQUAÇÕES ---


class Concrete:
    def __init__(self, fck, yc, cp_type=1):
        self.fck = fck
        self.yc = yc
        self.CP = cp_type

    def fckj(self, days=28):
        s = 0.25 if self.CP < 3 else (0.38 if self.CP < 5 else 0.20)
        betta = exp(s * (1 - (28 / days) ** 0.5))
        return betta * self.fck

    def fctm(self):
        return 0.3 * self.fckj() ** (2 / 3)

    def ecij(self, days=28):
        return 5600 * (self.fckj(days) ** (1 / 2))

    def ecs(self):
        fckj = self.fckj()
        return (0.8 + 0.2 * (fckj / 80)) * self.ecij()


class ReinforcedConcreteSection:
    def __init__(self, d_dict):
        self.concr = Concrete(d_dict["fck"], d_dict["yc"])
        self.Es = 210000  # MPa
        self.As = d_dict["as"]  # cm²
        self.b = d_dict["b"]  # cm
        self.h = d_dict["h"]  # cm
        self.cover = d_dict["cover"]  # cm
        self.L_cm = d_dict["gap"]  # cm (guardamos em cm para as fórmulas analíticas)
        self.L = d_dict["gap"] / 100.0  # metros (para o solver MEF)
        self.alpha_nbr = (
            1.2  # NBR 6118 sugere 1.2 para seções T ou 1.5 para retangulares
        )

    def d(self):
        return self.h - self.cover

    def alpha_e(self):
        return self.Es / self.concr.ecs()

    def inertia_1(self):
        return (self.b * self.h**3) / 12

    def x2(self):
        ae = self.alpha_e()
        a = self.b / 2
        b = ae * self.As
        c = -ae * self.As * self.d()
        roots = np.roots([a, b, c])
        return float(max(r.real for r in roots if 0 < r < self.h))

    def inertia_2(self):
        x = self.x2()
        return (self.b * x**3) / 3 + self.alpha_e() * self.As * (self.d() - x) ** 2

    def mcr(self):
        # fctm em MPa -> / 10 vira kN/cm²
        # Resultado em kN.cm
        fct_k_cm2 = self.concr.fctm() / 10.0
        return (self.alpha_nbr * fct_k_cm2 * self.inertia_1()) / (self.h / 2)

    def branson_inertia(self, ma_kn_cm):
        mr = abs(self.mcr())
        ma = abs(ma_kn_cm)

        if ma <= mr:
            return self.inertia_1()

        i1 = self.inertia_1()
        i2 = self.inertia_2()

        # Fórmula de Branson (NBR 6118:2014)
        m_ratio = (mr / ma) ** 3
        ie = m_ratio * i1 + (1 - m_ratio) * i2

        # A inércia efetiva não pode ser menor que a do Estádio II
        return max(ie, i2)

    def bischoff_inertia(self, ma_kn_cm):
        mr = abs(self.mcr())
        ma = abs(ma_kn_cm)

        if ma <= mr:
            return self.inertia_1()

        i1 = self.inertia_1()
        i2 = self.inertia_2()

        # Bischoff (frequentemente mais preciso que Branson para baixas taxas de armadura)
        return i2 / (1 - ((mr / ma) ** 2 * (1 - (i2 / i1))))

    def get_analytical_deflection(self, ma_kn_cm, inertia_type="branson"):
        """
        Cálculo da flecha máxima no centro do vão (Viga Biapoiada).
        Unidades: Ma (kN.cm), L (cm), E (kN/cm²), I (cm⁴) -> Resultado em cm
        """
        ma = abs(ma_kn_cm)
        i_eff = (
            self.branson_inertia(ma)
            if inertia_type == "branson"
            else self.bischoff_inertia(ma)
        )

        # Ecs em MPa -> / 10 vira kN/cm²
        ecs_k_cm2 = self.concr.ecs() / 10.0

        # Fórmula: 5/48 * (M * L²) / (E * I)
        return (5 * ma * (self.L_cm**2)) / (48 * ecs_k_cm2 * i_eff)
