def calcular_recompensa(hp, sp, mobs, accion, hp_anterior):
    recompensa = 0

    # Penalización por recibir daño
    if hp < hp_anterior:
        recompensa -= 5

    # Recompensa por usar poción con HP bajo
    if accion == "usar_pocion" and hp < 40:
        recompensa += 3

    # Recompensa por atacar cuando hay mobs
    if accion == "atacar" and mobs:
        recompensa += 5

    # Penalización por atacar sin mobs
    if accion == "atacar" and not mobs:
        recompensa -= 2

    # Huir con HP bajo es inteligente
    if accion == "huir" and hp < 30:
        recompensa += 5

    # Esperar sin necesidad o con mobs
    if accion == "esperar" and mobs:
        recompensa -= 3

    return recompensa
