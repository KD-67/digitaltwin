# Derives the arithmetic constants needed to normalize raw marker values.
# Given the healthy range boundaries, it computes the midpoint and half-width
# that the u-shaped health score transform uses to centre and scale raw values.


def compute_normalization_params(zone_boundaries: dict) -> dict:
    healthy_min = zone_boundaries["healthy_min"]
    healthy_max = zone_boundaries["healthy_max"]
    mid = (healthy_min + healthy_max) / 2.0
    half_range = (healthy_max - healthy_min) / 2.0
    return {
        "healthy_min": healthy_min,
        "healthy_max": healthy_max,
        "mid": mid,
        "half_range": half_range,
    }
