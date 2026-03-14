import csv
import os
from datetime import datetime

# Log path: configurable via environment variable
# Example: set PYROBOT_LOG_DIR=F:/GITHUB_REPOS/PyRoBot/logs
LOG_DIR = os.environ.get("PYROBOT_LOG_DIR", os.path.join(os.path.dirname(__file__), "..", "logs"))
LOG_PATH = os.path.join(LOG_DIR, "decision_history.csv")

# Asegura que la carpeta de logs exista
os.makedirs(LOG_DIR, exist_ok=True)

def inicializar_log():
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["timestamp", "hp", "sp", "mobs_detectados", "accion"])

def registrar_decision(hp, sp, mobs_detectados, accion):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # convierte cada caja a texto "x1_y1_x2_y2"
    mobs_str = ';'.join(f"{x1}_{y1}_{x2}_{y2}" for x1, y1, x2, y2 in mobs_detectados)
    with open(LOG_PATH, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, hp, sp, mobs_str, accion])

