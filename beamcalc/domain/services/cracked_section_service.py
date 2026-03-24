from utils.deflections import branson_equation


class CrackedSectionService:
    def get_effective_inertia(self, section, moment):
        return branson_equation(
            section.mcr(), moment, section.inertia_1(), section.inertia_2(), n=3
        )
