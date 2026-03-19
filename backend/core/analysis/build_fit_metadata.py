# Packages the polynomial fit results into the metadata dict that the frontend
# TrajectoryChart component needs to render the smooth fitted curve. The chart
# evaluates the polynomial client-side at many equally-spaced x-values, so it
# needs the raw coefficients, the reference timestamp t0, the polynomial degree,
# the normalization constants, and the zone boundary margin.

import numpy as np
from datetime import datetime


def build_fit_metadata(
    coeffs: np.ndarray,
    t0: datetime,
    polynomial_degree: int,
    zone_boundaries: dict,
) -> dict:
    healthy_min = zone_boundaries["healthy_min"]
    healthy_max = zone_boundaries["healthy_max"]
    mid         = (healthy_min + healthy_max) / 2.0
    half_range  = (healthy_max - healthy_min) / 2.0
    t0_iso      = t0.isoformat().replace("+00:00", "Z")

    return {
        "coefficients":      coeffs.tolist(),
        "t0_iso":            t0_iso,
        "polynomial_degree": polynomial_degree,
        "normalization": {
            "healthy_min": healthy_min,
            "healthy_max": healthy_max,
            "mid":         mid,
            "half_range":  half_range,
        },
        "zone_boundaries": {
            "vulnerability_margin": zone_boundaries["vulnerability_margin"],
        },
    }
