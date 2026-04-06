import json
import os
from datetime import datetime

def registrar_decision(hp, sp, mobs, accion):
    """
    Registra una decisión del bot en un archivo JSON.
    
    Args:
        hp: Porcentaje de HP actual
        sp: Porcentaje de SP actual
        mobs: Lista de mobs detectados
        accion: Acción tomada por el bot
    """
    historial_path = os.path.join(os.path.dirname(__file__), "..", "historial_decisions.json")
    
    # Cargar historial existente o crear uno nuevo
    try:
        with open(historial_path, 'r', encoding='utf-8') as f:
            historial = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        historial = []
    
    # Añadir nueva entrada
    entrada = {
        "timestamp": datetime.now().isoformat(),
        "hp": hp,
        "sp": sp,
        "mobs_count": len(mobs) if mobs else 0,
        "accion": accion
    }
    historial.append(entrada)
    
    # Guardar historial (limitado a las últimas 1000 entradas para no crecer indefinidamente)
    historial = historial[-1000:]
    with open(historial_path, 'w', encoding='utf-8') as f:
        json.dump(historial, f, indent=2)
