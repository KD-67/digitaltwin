# Converts a raw marker measurement into a health score on a u-shaped scale.
# The centre of the healthy range scores 1.0, the edges score 0.0, and anything
# outside the healthy range goes negative. This lets every marker be treated the
# same way regardless of whether "higher" or "lower" is healthier.


def normalize(raw: float, mid: float, half_range: float) -> float:
    return 1.0 - abs(raw - mid) / half_range
