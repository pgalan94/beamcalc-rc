from dataclasses import dataclass


@dataclass
class BeamAnalysis:
    name: str
    cases: dict

    def get_graph_dataframe(self):
        df = pd.DataFrame()
        load_arr = [
            0,
        ]
        moment_arr = [
            0,
        ]
        branson_arr = [
            0,
        ]
        bischoff_arr = [
            0,
        ]
        mef_arr = [
            0,
        ]
        for c in self.cases.values():
            load_arr.append(c.load)
            moment_arr.append(c.get_max_moment())
            branson_arr.append(c.branson)
            bischoff_arr.append(c.bischoff)
            mef_arr.append(c.get_max_deflection())
        df["load"] = load_arr
        df["moment"] = moment_arr
        df["branson"] = branson_arr
        df["bischoff"] = bischoff_arr
        df["mef"] = mef_arr
        return df

    def get_bending_diagram_dataframe(self, total_length):
        df = pd.DataFrame()
        last_case_key = max([k for k in self.cases.keys()])
        last_case = self.cases[last_case_key]
        bar_length = total_length / len(last_case.bars.keys())
        len_arr = []
        moment_arr = []
        for v in last_case.bars.values():
            len_arr.append((v.nodes[0].id - 1) * bar_length)
            moment_arr.append(v.nodes[0].M)
            if v.id == max([key for key in last_case.bars.keys()]):
                len_arr.append((v.nodes[1].id - 1) * bar_length)
                moment_arr.append(v.nodes[1].M)
        df["length"] = len_arr
        df["moment"] = moment_arr
        return df

    def get_shear_diagram_dataframe(self, total_length):
        df = pd.DataFrame()
        last_case_key = max([k for k in self.cases.keys()])
        last_case = self.cases[last_case_key]
        bar_length = total_length / len(last_case.bars.keys())
        len_arr = []
        shear_arr = []
        for v in last_case.bars.values():
            len_arr.append((v.nodes[0].id - 1) * bar_length)
            shear_arr.append(v.nodes[0].V)
            if v.id == max([key for key in last_case.bars.keys()]):
                len_arr.append((v.nodes[1].id - 1) * bar_length)
                shear_arr.append(v.nodes[1].V)
        df["length"] = len_arr
        df["shear"] = shear_arr
        return df


@dataclass
class LoadCaseObject:
    load: float
    bars: dict
    branson: float
    bischoff: float

    def get_node_deflection(self, node_id):
        return

    def get_node_moment(self):
        pass

    def get_max_deflection(self):
        max_uy = 0
        for b in self.bars.values():
            for n in b.nodes.values():
                if n.uy > max_uy:
                    max_uy = n.uy
        return max_uy

    def get_max_moment(self):
        max_moment = 0
        for b in self.bars.values():
            for n in b.nodes.values():
                if abs(n.M) > max_moment:
                    max_moment = abs(n.M)
        return max_moment


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
    nodes: dict

    def get_max_deflection(self):
        return max([n.uy for n in self.nodes.values()])

    def get_max_shear(self):
        return max([n.uy for n in self.nodes.values()])
