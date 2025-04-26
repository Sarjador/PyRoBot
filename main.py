import time
from core.capture import encontrar_ventana, capturar_client_area, get_client_rect
from core.detection import detectar_mobs
from core.hud_reader import leer_hp_sp
from core.actions import ejecutar_accion
from core.history_logger import inicializar_log, registrar_decision
from core.agent_rl import QLearningAgent
from core.rewards import calcular_recompensa

# Inicializa logger y agente RL
inicializar_log()
agente = QLearningAgent(actions=["atacar", "usar_pocion", "huir", "esperar"])

# Encuentra ventana de juego
ventana = encontrar_ventana()
if not ventana:
    print("No se encontró la ventana del juego.")
    exit()

# Obtén las dimensiones del área cliente (para debug)
left, top, width, height = get_client_rect(ventana._hWnd)
print(f"Client area: left={left}, top={top}, w={width}, h={height}")

print("Iniciando bot con IA por refuerzo... Ctrl+C para detener")
hp_anterior = 100
try:
    while True:
        # Captura SOLO el área cliente
        frame = capturar_client_area(ventana)

        # Detección y lectura de HUD
        mobs = detectar_mobs(frame)
        hp, sp = leer_hp_sp(frame)

        # Elección de acción
        estado = (hp, sp, len(mobs))
        accion = agente.choose_action(estado)

        # Ejecuta la acción (el módulo actions ya traduce coords cliente→pantalla)
        ejecutar_accion(accion, mobs)

        # Pequeña espera y captura siguiente estado
        time.sleep(0.2)
        frame_next = capturar_client_area(ventana)
        mobs_next = detectar_mobs(frame_next)
        hp_next, sp_next = leer_hp_sp(frame_next)
        next_state = (hp_next, sp_next, len(mobs_next))

        # Aprende y guarda
        recompensa = calcular_recompensa(hp_next, sp_next, mobs_next, accion, hp_anterior)
        agente.learn(estado, accion, recompensa, next_state)
        agente.save()

        # Registra para histórico
        registrar_decision(hp, sp, mobs, accion)
        print(f"HP: {hp}% | SP: {sp}% | Mobs: {mobs} -> Acción: {accion} | Recompensa: {recompensa}")

        hp_anterior = hp
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nBot detenido por el usuario.")
