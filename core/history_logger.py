import csv
import os
from datetime import datetime

#LOG_PATH = "../logs/decision_history.csv"
LOG_PATH = "F:/GITHUB_REPOS/PyRoBot/logs/decision_history.csv"
# Asegura que la carpeta de logs exista
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

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

