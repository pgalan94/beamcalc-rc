import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from beamcalc.infra.calculators.anastruct_adapter import AnastructSolverAdapter
from beamcalc.infra.database.sqlite_repository import SQLiteProjectRepository
from beamcalc.application.use_cases import BeamFactorService


def run_dashboard(df_results, beam_name):
    # Criamos dois subplots lado a lado
    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=(
            "Diagrama Carga x Flecha Máxima",
            "Momento Fletor (Última Etapa)",
        ),
        horizontal_spacing=0.15,
    )

    # --- GRÁFICO 1: CARGA X FLECHA (Estilo Figura 10 do legado) ---
    # MEF-Branson (Azul) - Multiplicamos por 100 se os dados no banco estiverem em metros
    fig.add_trace(
        go.Scatter(
            x=df_results["max_uy_mef"].abs() * 100,
            y=df_results["load_value"],
            name="MEF-Branson",
            line=dict(color="blue", width=3),
        ),
        row=1,
        col=1,
    )

    # Branson Analítico (Vermelho)
    fig.add_trace(
        go.Scatter(
            x=df_results["branson_analitico"].abs() * 100,
            y=df_results["load_value"],
            name="Branson Analítico",
            line=dict(color="red", dash="dash"),
        ),
        row=1,
        col=1,
    )

    # Bischoff Analítico (Verde)
    fig.add_trace(
        go.Scatter(
            x=df_results["bischoff_analitico"].abs() * 100,
            y=df_results["load_value"],
            name="Bischoff Analítico",
            line=dict(color="green", dash="dot"),
        ),
        row=1,
        col=1,
    )

    # --- GRÁFICO 2: MOMENTO FLETOR (Estilo Figura 11 do legado) ---
    last_step_nodes = df_results.iloc[-1]["nodes_json"]
    # Ordenar por x para evitar linhas cruzadas no gráfico
    nodes_sorted = sorted(last_step_nodes, key=lambda x: x["x"])

    fig.add_trace(
        go.Scatter(
            x=[n["x"] for n in nodes_sorted],
            y=[n["M"] for n in nodes_sorted],
            fill="tozeroy",
            name="Momento [kNm]",
            line=dict(color="royalblue"),
        ),
        row=1,
        col=2,
    )

    # --- FORMATAÇÃO GERAL ---
    fig.update_layout(
        title_text=f"Análise Estrutural ImediataVigas - Viga: {beam_name}",
        template="plotly_white",
        hovermode="x unified",
    )

    # Eixo Flecha x Carga
    fig.update_xaxes(title_text="Flecha Máxima (cm)", row=1, col=1)
    fig.update_yaxes(title_text="Carga Aplicada (kN/m)", row=1, col=1)

    # Eixo Vão x Momento (Invertido para padrão de engenharia)
    fig.update_xaxes(title_text="Vão (m)", row=1, col=2)
    fig.update_yaxes(title_text="Momento (kNm)", row=1, col=2, autorange="reversed")

    fig.show()


def main():
    # 1. Configurações da Viga (Input)
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
        "load_steps": 20,
        "discretization": 50,
    }

    # 2. Setup dos Componentes (Injeção de Dependência)
    repo = SQLiteProjectRepository(db_path="beam_analysis.db")
    solver = AnastructSolverAdapter()
    service = BeamFactorService(solver, repo)

    print(f"--- Iniciando análise da viga {beam_dict['name']} ---")

    # 3. Execução do Cálculo e Persistência
    # O service agora cria o ReinforcedConcreteSection e chama o IncrementalAnalysisService
    analysis = service.calculate_and_store(beam_dict)

    print("Cálculo finalizado e salvo no banco de dados.")

    # 4. Recuperação para Visualização
    # Pegamos o ID do último caso inserido para o Dashboard
    # (Em um sistema real, o service poderia retornar o case_id)
    print("Abrindo Dashboard no navegador...")
    # Buscamos os dados recém calculados
    df_results = repo.get_dashboard_data(case_id=1)  # Ou o ID gerado
    run_dashboard(df_results, "V101")


if __name__ == "__main__":
    main()
