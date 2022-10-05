import numpy as np
import pandas as pd


def laminar_flame_speed(v_u, v_b, rho_u, rho_b, stationary=False):
    """Calculates the laminar flame speed s_l for a 1d flame."""
    if stationary:
        # Flame front doesn't move
        flame_speed = v_b * rho_b / rho_u
    else:
        # There's an inlet of unburnt gas
        flame_speed = (v_b - v_u) / (rho_u / rho_b - 1)
    return flame_speed
