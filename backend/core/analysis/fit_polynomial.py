# Fits a polynomial of a given degree to time-indexed health score data and
# returns the coefficients alongside those of its first and second derivatives.
# The derivatives are precomputed here so callers can evaluate rate-of-change and
# curvature at any x without having to differentiate the polynomial themselves.

import numpy as np


def fit_polynomial(
    x_hours: list[float],
    h_values: list[float],
    polynomial_degree: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    min_points = polynomial_degree + 1
    if len(x_hours) < min_points:
        raise ValueError(
            f"A degree-{polynomial_degree} polynomial requires at least {min_points} "
            f"data points, but only {len(x_hours)} were provided."
        )

    x_arr = np.array(x_hours, dtype=float)
    y_arr = np.array(h_values, dtype=float)

    coeffs    = np.polyfit(x_arr, y_arr, polynomial_degree)
    coeffs_p1 = np.polyder(coeffs, 1)
    coeffs_p2 = np.polyder(coeffs, 2)

    return coeffs, coeffs_p1, coeffs_p2
