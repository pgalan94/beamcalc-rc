from beamcalc.infra.calculators.anastruct_adapter import AnastructSolverAdapter
from beamcalc.infra.database.sqlite_repository import SQLiteProjectRepository
from beamcalc.application.use_cases import BeamFactorService

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
    "q1": 60.00,
    "load_steps": 10,
    "discretization": 30,
}

service = BeamFactorService(
    AnastructSolverAdapter(), SQLiteProjectRepository(db_path="test.db")
)
analysis = service.calculate_and_store(beam_dict)
print("Sucesso! Verifique as tabelas 'cases', 'result_steps' e 'nodal_results' no DB.")
