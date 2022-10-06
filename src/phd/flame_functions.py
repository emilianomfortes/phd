import numpy as np
import pandas as pd
import json
import cantera as ct

# Flame functions
def laminar_flame_speed(v_u, v_b, rho_u, rho_b, stationary=False):
    """Calculates the laminar flame speed s_l for a 1d flame."""
    if stationary:
        # Flame front doesn't move
        flame_speed = v_b * rho_b / rho_u
    else:
        # There's an inlet of unburnt gas
        flame_speed = (v_b - v_u) / (rho_u / rho_b - 1)
    return flame_speed

def calculate_1d_points_in_grid(grid_LB, grid_RB, flame_thickness, n_flame_points):
    """Calculates the number of required points in a grid when
    a specific number of points is desidered within the flame front."""
    grid_length = grid_RB - grid_LB
    delta_x = flame_thickness / n_flame_points
    n_points = grid_length / delta_x
    print("delta", delta_x,"n_points", n_points)
    return n_points

# Dataframe functions
def df_paraview_to_fg(df, dim=3):
    """Translates column names from paraview .csv file to fg format"""
    possible_cols = ["VELOC:0", "Points:0", "DENSI", "TEMPE", "ZMEAN", "CMEAN"]
    flamegen_cols = ["u(m/s)", "x(m)", f"rho(kg/{dim})", "T(K)", "Z", "C"]
    df_cols = list(df.columns)

    for col, fg_col in zip(possible_cols, flamegen_cols):
        if col in df_cols:
            df = df.rename(columns={col: fg_col})
    return df 

# FG
def read_json(path_json):
    with open(path_json) as f:
        dict_json = json.load(f)
    return dict_json


def get_composition_from_dict(dictionary):

    _values = list(dictionary.values())
    _keys = list(dictionary.keys())    
    
    out_str = f"{_keys[0]}:{_values[0]}"
    for k, v in zip(_keys[1:], _values[1:]):
        out_str += f", {k}:{v}"
    return out_str

def gas_from_fg(fg_dict):
    """Creates a gas object from a FlameGenInputFile.json file."""
    equivalence_ratio = None

    # Read thermodynamic and transport data from FlameGen input file
    temperature = fg_dict["HeatLossData"]["Tf"]
    pressure = fg_dict["ChemistryData"]["pressure"]
    solution = fg_dict["ChemistryData"]["mechanism"]

    # Creates gas object based on FlameGen input file
    gas = ct.Solution(solution)

    # Read fuel and oxidizer composition from FlameGen input file
    _fuel = fg_dict["ChemistryData"]["fuelX"]
    _oxidizer = fg_dict["ChemistryData"]["oxidizerX"]

    fuel = get_composition_from_dict(_fuel)
    oxidizer = get_composition_from_dict(_oxidizer)
    reactants = fuel + ", " + oxidizer
    gas.TPX = temperature, pressure, reactants
    
    if fg_dict["FlameletTypeData"]["mixApproach"] == "phi":
        equivalence_ratio = fg_dict["FlameletTypeData"]["mixMethod"]
        gas.set_equivalence_ratio(equivalence_ratio, fuel=fuel, oxidizer=oxidizer)
    else:
        raise ValueError("Code only defined for phi mixing flamelet data")

    return gas