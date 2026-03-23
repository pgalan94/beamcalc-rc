from anastruct import SystemElements
from beamcalc.domain.models import NodeObject, BarObject


class AnastructSolverAdapter:
    def solve_beam(self, elements_config: list, supports: list, loads: list) -> dict:
        """
        Executa um único cálculo linear.
        elements_config: list of dicts {'start': [x,y], 'end': [x,y], 'EI': val}
        """
        ss = SystemElements()

        for el in elements_config:
            ss.add_element(location=[el["start"], el["end"]], EI=el["EI"])

        for sup in supports:
            if sup["type"] == "hinged":
                ss.add_support_hinged(node_id=sup["node_id"])

        for load in loads:
            ss.q_load(q=load["value"], element_id=load["element_id"])

        ss.solve()

        # Traduz os resultados brutos da anastruct para tipos básicos ou objetos de domínio
        results = {"bars": {}, "nodes": {}}
        for eid, elem in ss.element_map.items():
            results["bars"][eid] = {
                "M": [elem.bending_moment[0], elem.bending_moment[-1]],
                "V": [elem.shear_force[0], elem.shear_force[-1]],
                "node_ids": [elem.node_1.id, elem.node_2.id],
            }

        for nid, node in ss.node_map.items():
            results["nodes"][nid] = {"uy": node.uy, "phi": node.phi_z}

        return results
