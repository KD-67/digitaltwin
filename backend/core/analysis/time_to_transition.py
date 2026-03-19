# Predicts when a health trajectory will next cross a zone boundary by finding
# the nearest future root of the fitted polynomial relative to each boundary value.
# Returns the time in hours from t0, or None if the polynomial never crosses a
# boundary beyond the current position (e.g. a flat or fully contained curve).

import numpy as np

IMAGINARY_TOLERANCE = 1e-6


def time_to_transition(
    coeffs: np.ndarray,
    vulnerability_margin: float,
    x_current: float,
) -> float | None:
    candidate_times = []
    for boundary_value in (vulnerability_margin, 0.0, -vulnerability_margin):
        shifted = coeffs.copy()
        shifted[-1] -= boundary_value
        roots = np.roots(shifted)
        for root in roots:
            if abs(root.imag) > IMAGINARY_TOLERANCE:
                continue
            t = root.real
            if t > x_current:
                candidate_times.append(t)
    return float(min(candidate_times)) if candidate_times else None
