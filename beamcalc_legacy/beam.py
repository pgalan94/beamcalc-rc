from .sections import RectangularSection, ReinforcedConcreteSection
from .materials import ReinforcedConcrete, Concrete, Rebar
from .analysis import BeamAnalysis, NodeObject, BarObject
from .elements import Node, Bar, Support
from anastruct import SystemElements, Vertex
import numpy as np
from math import ceil
from .deflections import branson_equation


class Beam:

    @staticmethod
    def create_beam_from_dict(input_dict):
        section_geometry = RectangularSection(input_dict["b"], input_dict["h"])
        section_material = ReinforcedConcrete(
            Concrete(input_dict["fck"], input_dict["yc"], input_dict["gamma"], 1),
            Rebar(500, 1.15, 7850, 210000, input_dict["as"], input_dict["asl"]),
        )
        section = ReinforcedConcreteSection(
            section_material, section_geometry, input_dict["cover"]
        )
        total_len = input_dict["gap"]
        x = 0
        last_node = Node(0, 0)
        node_dict = {"0,0": last_node}
        nodes = [
            last_node,
        ]
        length_step = input_dict["discretization"]
        elements_dict = {}
        while x < total_len:
            x += length_step
            new_node = Node(x, 0)
            elements_dict[x / length_step] = Bar(
                last_node, new_node, section.ea(), section.ei1()
            )
            nodes.append(new_node)
            node_dict[str(new_node)] = new_node
            last_node = new_node
        supports = [
            Support(node_dict["0,0"], True, True, False),
            Support(node_dict[f"%d,0" % input_dict["gap"]], True, True, False),
        ]
        load = -input_dict["q1"] / 100
        beam_name = input_dict["name"]
        b = Beam(
            beam_name,
            nodes,
            supports,
            section,
            load,
            input_dict["discretization"],
            input_dict["load_steps"],
            elements=elements_dict,
            data=input_dict,
        )
        return b

    def __init__(
        self,
        name: str,
        nodes: list,
        sups: list,
        section: ReinforcedConcreteSection,
        q_load: float,
        discretization: int,
        load_step: float,
        elements: dict = None,
        data=None,
        analysis: BeamAnalysis = None,
    ):
        self.name = name
        self.nodes = nodes
        self.supports = sups
        self.section = section
        self.q_load = q_load
        self.discretization = discretization
        self.load_step = load_step
        self.ss = SystemElements()
        self.total_length = np.linalg.norm(np.array(nodes[-1].coords) - [0.0, 0.0])
        self.solved = False
        self.branson_deflection = 0
        self.bischoff_deflection = 0
        self.analysis = analysis
        if elements is None:
            elements = {}
        self.elements = elements
        if data is None:
            data = []
        self.data = data

    def get_analysis_data(self):
        dataframes = []
        for case in self.analysis.cases.values():
            df = {}
            if not self.solved:
                return dataframes
            df["element"] = [x for x in case.bars.keys()]
            bars = case.bars.values()
            df["ei"] = [el.EI for el in bars]
            df["ea"] = [el.EA for el in bars]
            df["shear"] = [el.nodes[0].V for el in bars]
            df["shear_2"] = [el.nodes[1].V for el in bars]
            df["moment"] = [el.nodes[0].M for el in bars]
            df["moment_2"] = [el.nodes[1].M for el in bars]
            df["uy"] = [el.nodes[0].uy * 10 for el in bars]
            df["uy_2"] = [el.nodes[1].uy * 10 for el in bars]
            df["phi"] = [el.nodes[0].phi for el in bars]
            df["phi_2"] = [el.nodes[1].phi for el in bars]
            df["cracked"] = [x in self.cracked_elements().keys() for x in df["element"]]
            dataframes.append(df)
        return dataframes

    def branson_inertia(self, actual_moment):
        ief = branson_equation(
            abs(self.section.mcr()),
            abs(actual_moment),
            self.section.inertia1(),
            self.section.inertia2(),
            n=4,
        )
        return ief

    def ei_br(self, actual_moment):
        effective_stiffness = (
            self.branson_inertia(actual_moment) * self.section.material.concrete.ecs()
        )
        return effective_stiffness

    def add_elements(self):
        for ele in self.nodes:
            if ele == Node(0, 0):
                continue
            self.ss.add_element(
                location=[ele.coords], EA=self.section.ea(), EI=self.section.ei1()
            )
        for sup in self.supports:
            n = self.ss.find_node_id(Vertex(sup.node.coords))
            if not any(self.ss.supports_fixed):
                self.ss.add_support_hinged(node_id=n)
                continue
            self.ss.add_support_roll(node_id=n)

    def add_elements_from_dict(self):
        for k, v in self.elements.items():
            if k == 0:
                continue
            self.ss.add_element(location=[v.coords()], EA=v.EA, EI=v.EI)
        for sup in self.supports:
            if not any(self.ss.supports_fixed):
                n = self.ss.find_node_id(Vertex(sup.node.coords))
                self.ss.add_support_hinged(node_id=n)
                continue
            n = self.ss.find_node_id(Vertex(sup.node.coords))
            self.ss.add_support_roll(node_id=n)

    def cracked_elements(self):
        elements = {}
        if not self.solved:
            return elements
        for k, v in self.ss.element_map.items():
            if (abs(v.bending_moment[0]) > abs(self.section.mcr())) or (
                abs(v.bending_moment[-1]) > abs(self.section.mcr())
            ):
                start_node = Node(*v.vertex_1.coordinates)
                end_node = Node(*v.vertex_2.coordinates)
                moment_in_act = max(abs(v.bending_moment[0]), abs(v.bending_moment[-1]))
                elements[k] = Bar(
                    start_node,
                    end_node,
                    int(self.section.ea()),
                    ceil(self.ei_br(moment_in_act) / 100) * 100,
                )
        return elements

    def get_max_deflection_value(self):
        if not self.solved:
            return 0
        return max([node.uy for node in self.ss.node_map.values()])

    def solve_beam(self, load=0):
        if load == 0:
            load = self.q_load
        for k in self.ss.element_map.keys():
            self.ss.q_load(q=load, element_id=k)
        self.ss.solve()
        self.solved = True
        return self.solved

    def create_analysis_bars_and_nodes(self, load_case_object):
        bar_dict = self.ss.element_map
        cracked_elements = self.cracked_elements()
        i = 1
        for k, v in bar_dict.items():
            x = 0
            new_nodes = {}
            for kk, vv in v.node_map.items():
                new_nodes[x] = NodeObject(
                    int(vv.id),
                    float(vv.Fy),
                    float(vv.Tz),
                    float(vv.uy),
                    float(vv.phi_z),
                )
                x += 1

            new_bar = BarObject(
                v.id, v.EI, v.EA, bool(v.id in cracked_elements), new_nodes
            )
            load_case_object.bars[new_bar.id] = new_bar
        return load_case_object
