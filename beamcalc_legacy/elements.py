from dataclasses import dataclass
import numpy as np


class Node:
    def __init__(self, xx, yy):
        self.xx = xx
        self.yy = yy
        self.coords = np.array([xx, yy])

    def __str__(self):
        return f"%d,%d" % (self.xx, self.yy)

    def __repr__(self):
        return f"%d,%d" % (self.xx, self.yy)

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.xx == other.xx and self.yy == other.yy


@dataclass
class Bar:
    node_a: Node
    node_b: Node
    EA: int
    EI: int

    def length(self):
        return np.linalg.norm(self.node_a.coords - self.node_b.coords)

    def coords(self):
        return self.node_b.coords


@dataclass
class Support:
    node: Node
    xx: bool
    yy: bool
    zz: bool
