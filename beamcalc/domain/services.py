from beamcalc.domain.models import BeamAnalysis, LoadCaseObject, BarObject, NodeObject


class IncrementalAnalysisService:
    def __init__(self, solver_adapter, section_model):
        self.solver = solver_adapter
        self.sect = section_model  # O modelo da seção já conhece L, fck, As, etc.

    def run_analysis(self, d_dict):
        analysis = BeamAnalysis(d_dict["name"])

        n_steps = int(d_dict["load_steps"])
        discretization = int(d_dict["discretization"])

        # 1. Padronização de unidades: m e kN
        L_meters = self.sect.L / 100.0  # Converte cm para m
        step_len = L_meters / discretization
        q_total = d_dict["q1"]  # kN/m

        # Estado inicial: Estádio I (Rígido)
        # EI = Ecs * Ic
        ei_initial = self.sect.concr.ecs() * self.sect.inertia_1()
        current_ei_map = {i + 1: ei_initial for i in range(discretization)}

        for i in range(1, n_steps + 1):
            q_current = (q_total / n_steps) * i

            # 2. Montagem da Malha para o Solver
            elements = self._build_elements(discretization, step_len, current_ei_map)
            supports = self._build_supports(discretization)
            loads = [
                {"element_id": j + 1, "value": -q_current}
                for j in range(discretization)
            ]

            # 3. Solver (Cálculo Linear com a rigidez do passo anterior)
            raw_res = self.solver.solve_beam(elements, supports, loads)

            # 4. Processamento de Resultados e Atualização de Rigidez (Branson)
            step_bars = {}
            max_m_step = 0

            for eid, res_bar in raw_res["bars"].items():
                # Pegamos o momento máximo deste elemento para atualizar sua rigidez
                # Nota: res_bar["M"] vem do solver em kN.m
                m_element = max(abs(res_bar["M"][0]), abs(res_bar["M"][1]))
                max_m_step = max(max_m_step, m_element)

                # Atualiza rigidez para o PRÓXIMO step (O coração do MEF-Branson)
                # Passamos o momento em kN.cm para a função branson se ela esperar cm
                current_ei_map[eid] = self.sect.concr.ecs() * self.sect.branson_inertia(
                    m_element * 100.0
                )

                # Mapeia para Objetos de Domínio
                step_bars[eid] = self._create_bar_object(
                    eid, res_bar, raw_res["nodes"], current_ei_map[eid]
                )

            # 5. Cálculos Analíticos Globais (Para as 3 linhas do gráfico)
            # Momentos convertidos para kN.cm para bater com as fórmulas de norma
            m_max_kncm = (q_current * (L_meters**2) / 8.0) * 100.0

            analysis.cases[q_current] = LoadCaseObject(
                load=q_current,
                bars=step_bars,
                branson=self.sect.get_analytical_deflection(m_max_kncm, "branson"),
                bischoff=self.sect.get_analytical_deflection(m_max_kncm, "bischoff"),
            )

        return analysis

    def _build_elements(self, disc, step_len, ei_map):
        return [
            {
                "start": [n * step_len, 0],
                "end": [(n + 1) * step_len, 0],
                "EI": ei_map[n + 1],
            }
            for n in range(disc)
        ]

    def _build_supports(self, disc):
        return [
            {"node_id": 1, "type": "hinged"},
            {"node_id": disc + 1, "type": "hinged"},
        ]

    def _create_bar_object(self, eid, res_bar, raw_nodes, current_ei):
        nodes = {}
        for idx, nid in enumerate(res_bar["node_ids"]):
            n_data = raw_nodes[nid]
            nodes[idx] = NodeObject(
                nid,
                res_bar["V"][idx],
                res_bar["M"][idx],
                n_data["uy"] * 100.0,  # Converte flecha de m para cm para o gráfico
                n_data["phi"],
            )
        return BarObject(eid, current_ei, 0.0, False, nodes)
