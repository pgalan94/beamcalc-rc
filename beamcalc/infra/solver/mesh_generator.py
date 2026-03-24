from dataclasses import dataclass
from typing import List


@dataclass
class MeshNode:
    id: int
    x: float
    y: float = 0.0


@dataclass
class MeshElement:
    id: int
    node_start: int
    node_end: int


@dataclass
class Mesh:
    nodes: List[MeshNode]
    elements: List[MeshElement]


class MeshGenerator:
    def __init__(self, step: float):
        self.step = step

    def generate(self, beam) -> Mesh:
        """
        Converte um Beam (domínio) em uma malha 1D.
        """

        length = beam.length

        if self.step <= 0:
            raise ValueError("Discretization step must be > 0")

        nodes = []
        elements = []

        # 🧱 gerar nós
        x = 0.0
        node_id = 0

        while x < length:
            nodes.append(MeshNode(id=node_id, x=x))
            x += self.step
            node_id += 1

        # garantir último nó exatamente no final
        if nodes[-1].x < length:
            nodes.append(MeshNode(id=node_id, x=length))

        # 🔗 gerar elementos
        for i in range(len(nodes) - 1):
            elements.append(
                MeshElement(
                    id=i,
                    node_start=nodes[i].id,
                    node_end=nodes[i + 1].id,
                )
            )

        return Mesh(nodes=nodes, elements=elements)
