from .analysis import BeamAnalysis, LoadCaseObject
from .beam import Beam
from .deflections import get_branson_deflection, get_bischoff_deflection


def solve_beam_incrementally(original_beam, load_step):
    beam_analysis = BeamAnalysis(original_beam.name, {})
    if original_beam.q_load < 0:
        load_step *= -0.01
    load = load_step
    already_cracked_elements = {}
    beam_elements = original_beam.elements
    beam = None
    new_name = ""
    while abs(load) <= round(abs(original_beam.q_load + load_step / 2), 4):
        new_load_case = LoadCaseObject(abs(load), {}, 0.0, 0.0)
        if new_name == original_beam.name + "L" + str(load):
            new_name = new_name + "+1"
        else:
            new_name = original_beam.name + "L{:.5f}".format(load)
        beam = Beam(
            new_name,
            original_beam.nodes,
            original_beam.supports,
            original_beam.section,
            load,
            original_beam.discretization,
            original_beam.load_step,
            beam_elements,
            original_beam.data,
        )
        beam.add_elements_from_dict()
        beam.solve_beam()
        ma = abs(beam.q_load * beam.total_length**2) / 8
        if (ma != 0) and (ma > beam.section.mcr()):
            beam.branson_deflection = get_branson_deflection(
                beam.total_length,
                beam.section.material.concrete.ecs(),
                abs(beam.section.mcr()),
                abs(ma),
                abs(beam.section.inertia1()),
                abs(beam.section.inertia2()),
            )
            beam.bischoff_deflection = get_bischoff_deflection(
                beam.total_length,
                beam.section.material.concrete.ecs(),
                abs(beam.section.mcr()),
                abs(ma),
                abs(beam.section.inertia1()),
                abs(beam.section.inertia2()),
            )
            new_load_case.branson = beam.branson_deflection
            new_load_case.bischoff = beam.bischoff_deflection
        else:
            beam.branson_deflection = beam.get_max_deflection_value()
            beam.bischoff_deflection = beam.get_max_deflection_value()
            new_load_case.branson = beam.branson_deflection
            new_load_case.bischoff = beam.bischoff_deflection
        new_load_case = beam.create_analysis_bars_and_nodes(new_load_case)
        beam_analysis.cases[new_load_case.load] = new_load_case
        new_cracked_elements = beam.cracked_elements()
        if new_cracked_elements != {}:
            if already_cracked_elements == {}:
                already_cracked_elements = new_cracked_elements
            elif new_cracked_elements == already_cracked_elements:
                load += load_step
            elif len(new_cracked_elements) < len(already_cracked_elements):
                load += load_step
            else:
                if new_cracked_elements.keys() == already_cracked_elements.keys():
                    step = True
                    for k in new_cracked_elements.keys():
                        if new_cracked_elements[k].EI == already_cracked_elements[k].EI:
                            continue
                        else:
                            if (
                                new_cracked_elements[k].EI
                                < already_cracked_elements[k].EI
                            ):
                                step = False
                    if step:
                        load += load_step
                already_cracked_elements.update(new_cracked_elements)
        else:
            load += load_step
        beam_elements.update(already_cracked_elements)
    if beam is not None:
        beam.name = original_beam.name
        beam.analysis = beam_analysis
        beam.solved = True
        return beam
    return None
