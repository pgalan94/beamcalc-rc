from beamcalc.domain.models import ReinforcedConcreteSection
from beamcalc.domain.services import IncrementalAnalysisService


class BeamFactorService:
    def __init__(self, solver_adapter, repository):
        """
        solver_adapter: O adaptador da Anastruct (infra)
        repository: O repositório SQLite (infra)
        """
        self.solver_adapter = solver_adapter
        self.repository = repository

    def calculate_and_store(self, beam_dict):
        # 1. Instancia o modelo de domínio da seção com os dados do dicionário
        section_model = ReinforcedConcreteSection(beam_dict)

        # 2. Instancia o serviço de domínio que detém a lógica de Branson/Incremental
        analysis_service = IncrementalAnalysisService(
            solver_adapter=self.solver_adapter, section_model=section_model
        )

        # 3. Executa a análise (Regra de Negócio)
        analysis = analysis_service.run_analysis(beam_dict)

        # 4. Persiste os resultados (Infraestrutura)
        self.repository.save_full_project(beam_dict, analysis)

        return analysis
