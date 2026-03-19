# Runs the complete trajectory analysis for a single data point given a fitted
# polynomial. Evaluates the polynomial and both of its derivatives at the point's
# x-coordinate, assigns a zone and derivative sign classes, looks up the 27-state
# trajectory label, and estimates when the trajectory will next cross a zone boundary.

import numpy as np

from .assign_zone_from_score import assign_zone_from_score
from .sign_class import sign_class
from .trajectory_state import trajectory_state
from .time_to_transition import time_to_transition


def analyze_datapoint(
    x: float,
    raw_value: float,
    h: float,
    data_quality: str,
    measured_at: str,
    coeffs: np.ndarray,
    coeffs_p1: np.ndarray,
    coeffs_p2: np.ndarray,
    vulnerability_margin: float,
) -> dict:
    fitted_value   = float(np.polyval(coeffs, x))
    f_prime        = float(np.polyval(coeffs_p1, x))
    f_double_prime = float(np.polyval(coeffs_p2, x))

    zone     = assign_zone_from_score(h, vulnerability_margin)
    fp_sign  = sign_class(f_prime)
    fpp_sign = sign_class(f_double_prime)
    state    = trajectory_state(zone, fp_sign, fpp_sign)
    transition = time_to_transition(coeffs, vulnerability_margin, x)

    return {
        "timestamp":                measured_at,
        "x_hours":                  round(x, 6),
        "raw_value":                raw_value,
        "data_quality":             data_quality,
        "health_score":             round(h, 6),
        "fitted_value":             round(fitted_value, 6),
        "zone":                     zone,
        "f_prime":                  round(f_prime, 6),
        "f_double_prime":           round(f_double_prime, 6),
        "trajectory_state":         state,
        "time_to_transition_hours": round(transition, 4) if transition is not None else None,
    }
