from typing import List, Dict
import random

class BotDecisionSystem:
    def __init__(self):
        self.history = []  # Guarda observaciones y acciones

    def decidir_accion(self, hp: int, sp: int, mobs_detectados: List[str]) -> str:
        """
        Toma una decisión en base a las observaciones actuales.
        """
        estado = {
            "hp": hp,
            "sp": sp,
            "mobs_detectados": mobs_detectados,
            "num_mobs": len(mobs_detectados)
        }

        # Reglas básicas
        if hp < 30:
            accion = "usar_pocion"
        elif estado["num_mobs"] >= 3 and hp < 50:
            accion = "huir"
        elif any(mob in ["familiar", "high_orc", "mvp_orc_lord", "npc", "orc_archer", "orc_baby", "orc_lady",
                         "orc_skeleton", "orc_warrior", "orc_zombie", "plant_blue", "plant_green", "plant_red",
                         "plant_white", "plant_yellow", "poison_spore", "red_mushroom", "black_mushroom", "roda_frog",
                         "spore", "stainer", "steel_chonchon", "willow", "worm tail", "zenorc", "bigfoot", "boa",
                         "caramel", "chonchon", "creamy", "drainliar", "elder_willow"] for mob in mobs_detectados):
            accion = "atacar"
        else:
            accion = "esperar"

        # Guardamos la observación y la acción tomada
        self.history.append({"estado": estado, "accion": accion})

        return accion

    def mostrar_historial(self):
        for entrada in self.history:
            print(f"Estado: {entrada['estado']} -> Acción: {entrada['accion']}")

# Ejemplo de uso
decisor = BotDecisionSystem()
accion = decisor.decidir_accion(hp=25, sp=40, mobs_detectados=["poring", "fabre"])
print(f"Acción tomada: {accion}")

decisor.mostrar_historial()
