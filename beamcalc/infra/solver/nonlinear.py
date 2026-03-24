from copy import deepcopy

from .anastruct_solver import AnastructSolver
from .mesh_generator import MeshGenerator
from domain.physics.deflection import (
    BransonModel,
    DeflectionCalculator,
    SectionProperties,
)


class NonLinearSolver:
    def __init__(self, step: float):
        self.step = step
        self.linear_solver = AnastructSolver()
        self.mesh_generator = MeshGenerator(step)
        self.branson = BransonModel()

    def solve(self, beam):
        mesh = self.mesh_generator.generate(beam)

        load = self.step
        target_load = beam.loads[0].value  # simplificação

        cracked_elements = {}
        results = {}

        while abs(load) <= abs(target_load):

            # ========================
            # 1. CLONAR BEAM
            # ========================
            current_beam = deepcopy(beam)
            current_beam.loads[0].value = load

            # ========================
            # 2. RESOLVER LINEAR
            # ========================
            result = self.linear_solver.solve(
                current_beam, mesh, ei_override=cracked_elements
            )
            # ========================
            # 3. CALCULAR MA GLOBAL
            # ========================
            L = beam.length
            ma = abs(load * L**2) / 8

            props = SectionProperties(
                inertia_uncracked=beam.section.inertia,
                inertia_cracked=beam.section.inertia_cracked,
                mr=beam.section.mcr,
                ecs=beam.section.ecs,
            )

            # ========================
            # 4. AVALIAR FISSURAÇÃO
            # ========================
            new_cracked = {}

            for el_id, el in result["elements"].items():
                m_max = max(abs(el["moment_start"]), abs(el["moment_end"]))

                if m_max > props.mr:
                    ie = self.branson.effective_inertia(props, m_max)

                    new_cracked[el_id] = ie

            # ========================
            # 5. ATUALIZAR RIGIDEZ (REGRA DO LEGADO)
            # ========================
            if new_cracked:
                if not cracked_elements:
                    cracked_elements = new_cracked

                elif new_cracked.keys() != cracked_elements.keys():
                    cracked_elements.update(new_cracked)

                else:
                    stable = True
                    for k in new_cracked:
                        if new_cracked[k] < cracked_elements[k]:
                            stable = False

                    if stable:
                        load += self.step

            else:
                load += self.step

            # ========================
            # 6. ARMAZENAR RESULTADO
            # ========================
            results[load] = result

        return results
