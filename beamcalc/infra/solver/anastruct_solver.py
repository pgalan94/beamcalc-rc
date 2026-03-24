from dataclasses import dataclass
from typing import Dict, Optional

from anastruct import SystemElements, Vertex
from .mesh_generator import Mesh
from math import ceil


def normalize_ei(ei: float) -> float:
    return ceil(ei / 100) * 100


# ========================
# RESULT MODELS
# ========================


@dataclass
class NodeResult:
    id: int
    ux: float
    uy: float
    phi: float


@dataclass
class ElementResult:
    id: int
    moment_start: float
    moment_end: float
    shear_start: float
    shear_end: float


@dataclass
class BeamResult:
    nodes: Dict[int, NodeResult]
    elements: Dict[int, ElementResult]


# ========================
# SOLVER
# ========================


class AnastructSolver:
    def solve(
        self,
        beam,
        mesh: Mesh,
        ei_override: Optional[Dict[int, float]] = None,
    ) -> BeamResult:

        ss = SystemElements()

        if ei_override is None:
            ei_override = {}

        # ========================
        # 1. CRIAR ELEMENTOS
        # ========================
        node_map = {node.id: node for node in mesh.nodes}

        for element in mesh.elements:
            n1 = node_map[element.node_start]
            n2 = node_map[element.node_end]

            EI_raw = ei_override.get(element.id, beam.section.inertia)
            EI = normalize_ei(EI_raw)

            ss.add_element(
                location=[[n1.x, n1.y], [n2.x, n2.y]],
                EA=beam.section.area,
                EI=EI,
            )

        # ========================
        # 2. APLICAR APOIOS
        # ========================
        for support in beam.supports:
            vertex = Vertex([support.position, 0.0])
            node_id = ss.find_node_id(vertex)

            if support.type == "hinged":
                ss.add_support_hinged(node_id=node_id)
            elif support.type == "roller":
                ss.add_support_roll(node_id=node_id)
            elif support.type == "fixed":
                ss.add_support_fixed(node_id=node_id)

        # ========================
        # 3. APLICAR CARGAS
        # ========================
        for load in beam.loads:
            for el_id in ss.element_map.keys():
                ss.q_load(q=load.value, element_id=el_id)

        # ========================
        # 4. RESOLVER
        # ========================
        ss.solve()

        # ========================
        # 5. EXTRAIR RESULTADOS
        # ========================
        node_results = {}
        for node_id, node in ss.node_map.items():
            node_results[node_id] = NodeResult(
                id=node_id,
                ux=node.ux,
                uy=node.uy,
                phi=node.phi_z,
            )

        element_results = {}
        for el_id, el in ss.element_map.items():
            element_results[el_id] = ElementResult(
                id=el_id,
                moment_start=el.bending_moment[0],
                moment_end=el.bending_moment[-1],
                shear_start=el.shear_force[0],
                shear_end=el.shear_force[-1],
            )

        return BeamResult(
            nodes=node_results,
            elements=element_results,
        )
