from beamcalc import Beam, solve_beam_incrementally

beam_dict = {
    "name": "V101",
    "fck": 50,
    "yc": 1.4,
    "gamma": 2500,
    "v": 0.2,
    "alpha": 1e-5,
    "b": 20,
    "h": 40,
    "as": 2.50,
    "asl": 2.50,
    "cover": 5.00,
    "gap": 300.00,
    "q1": 30.00,
    "load_steps": 10.00,
    "discretization": 30,
}

beam = Beam.create_beam_from_dict(beam_dict)
beam.add_elements()
solved_beam = solve_beam_incrementally(beam, beam_dict["load_steps"])

dfs = solved_beam.get_analysis_data()
