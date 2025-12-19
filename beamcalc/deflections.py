def get_branson_deflection(length, ecs, mr, ma, inertia_1, inertia_2):
    return (5 * ma * length**2) / (
        48 * (ecs / 10) * branson_equation(mr, ma, inertia_1, inertia_2)
    )


def branson_equation(mr, ma, inertia_1, inertia_2, n=3):
    effective_inertia = (mr / ma) ** n * inertia_1 + (1 - (mr / ma) ** n) * inertia_2
    return effective_inertia


def get_bischoff_deflection(length, ecs, mr, ma, inertia_1, inertia_2):
    return (5 * ma * length**2) / (
        48 * (ecs / 10) * bischoff_equation(mr, ma, inertia_1, inertia_2)
    )


def bischoff_equation(mr, ma, inertia_1, inertia_2):
    effective_inertia = inertia_2 / (
        1 - (((mr / ma) ** 2) * (1 - (inertia_2 / inertia_1)))
    )
    return effective_inertia
