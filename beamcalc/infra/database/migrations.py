def get_migrations():
    return [
        """CREATE TABLE IF NOT EXISTS material (id INTEGER PRIMARY KEY, fck REAL, yc REAL, gamma REAL, v REAL)""",
        """CREATE TABLE IF NOT EXISTS section (id INTEGER PRIMARY KEY, b REAL, height REAL, as_pos REAL, asl_neg REAL, cover REAL)""",
        """CREATE TABLE IF NOT EXISTS beam (id INTEGER PRIMARY KEY, name TEXT, gap REAL, mat_id INTEGER, sec_id INTEGER)""",
        """CREATE TABLE IF NOT EXISTS cases (id INTEGER PRIMARY KEY, beam_id INTEGER, q1 REAL, steps INTEGER, discretization INTEGER)""",
        """CREATE TABLE IF NOT EXISTS result_steps (id INTEGER PRIMARY KEY, case_id INTEGER, load_step_index INTEGER, load_value REAL, branson REAL, bischoff REAL)""",
        """CREATE TABLE IF NOT EXISTS nodal_results (id INTEGER PRIMARY KEY, step_id INTEGER, node_id INTEGER, x_coord REAL, shear REAL, moment REAL, deflection REAL, is_cracked INTEGER)""",
    ]
