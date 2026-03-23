import sqlite3
import pandas as pd
import json
from .migrations import get_migrations


class SQLiteProjectRepository:
    def __init__(self, db_path="beamcalc.db"):
        self.db_path = db_path
        self._run_migrations()

    def _run_migrations(self):
        with sqlite3.connect(self.db_path) as conn:
            for sql in get_migrations():
                conn.execute(sql)

    def save_full_project(self, d, analysis):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()

            # 1. Cadastro de Inputs
            cur.execute(
                "INSERT INTO material (fck, yc, gamma, v) VALUES (?,?,?,?)",
                (d["fck"], d["yc"], d["gamma"], d["v"]),
            )
            mat_id = cur.lastrowid

            cur.execute(
                "INSERT INTO section (b, height, as_pos, asl_neg, cover) VALUES (?,?,?,?,?)",
                (d["b"], d["h"], d["as"], d["asl"], d["cover"]),
            )
            sec_id = cur.lastrowid

            cur.execute(
                "INSERT INTO beam (name, gap, mat_id, sec_id) VALUES (?,?,?,?)",
                (d["name"], d["gap"], mat_id, sec_id),
            )
            beam_id = cur.lastrowid

            cur.execute(
                "INSERT INTO cases (beam_id, q1, steps, discretization) VALUES (?,?,?,?)",
                (beam_id, d["q1"], d["load_steps"], d["discretization"]),
            )
            case_id = cur.lastrowid

            # 2. Salvar Resultados Incrementais
            for i, (load, case_obj) in enumerate(analysis.cases.items()):
                cur.execute(
                    "INSERT INTO result_steps (case_id, load_step_index, load_value, branson, bischoff) VALUES (?,?,?,?,?)",
                    (case_id, i, load, case_obj.branson, case_obj.bischoff),
                )
                step_id = cur.lastrowid

                # Coleta dados de todos os nós sem duplicar (nós compartilhados entre elementos)
                node_results_to_save = {}

                for bar in case_obj.bars.values():
                    is_cracked = 1 if bar.cracked else 0
                    for local_idx, n in bar.nodes.items():
                        # Se o nó já foi processado nesta etapa, mantemos o maior esforço ou apenas ignoramos
                        if n.id not in node_results_to_save:
                            # x_coord pode ser calculado ou extraído se disponível
                            node_results_to_save[n.id] = (
                                step_id,
                                n.id,
                                0.0,
                                n.V,
                                n.M,
                                n.uy,
                                is_cracked,
                            )

                cur.executemany(
                    "INSERT INTO nodal_results (step_id, node_id, x_coord, shear, moment, deflection, is_cracked) VALUES (?,?,?,?,?,?,?)",
                    list(node_results_to_save.values()),
                )

            conn.commit()  # Essencial para persistir os dados

    def get_dashboard_data(self, case_id):
        # O group_concat ou json_group_array organiza os nós para o gráfico de momentos
        query = """
        SELECT 
            rs.load_value,
            rs.branson AS branson_analitico,
            rs.bischoff AS bischoff_analitico,
            (SELECT MIN(deflection) FROM nodal_results WHERE step_id = rs.id) AS max_uy_mef,
            json_group_array(
                json_object(
                    'x', nr.x_coord, 
                    'M', nr.moment
                )
            ) as nodes_json
        FROM result_steps rs
        JOIN nodal_results nr ON rs.id = nr.step_id
        WHERE rs.case_id = ?
        GROUP BY rs.id
        ORDER BY rs.load_value ASC
        """
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(query, conn, params=(case_id,))
            # Decodifica o JSON dos nós para plotar o diagrama de momentos
            df["nodes_json"] = df["nodes_json"].apply(json.loads)
            return df
