# Combines a data point's zone and the signs of the first and second derivatives
# into a single integer from 1 to 27 that uniquely identifies its trajectory state.
# The 27 states come from 3 zones × 3 first-derivative classes × 3 second-derivative
# classes, giving a compact label for every possible combination of "where you are"
# and "how fast and in which direction you're moving".

_ZONE_OFFSET = {1: 0, 0: 9, -1: 18}
_FP_OFFSET   = {1: 0, 0: 3, -1: 6}
_FPP_INDEX   = {1: 1, 0: 2, -1: 3}


def trajectory_state(zone: str, fp_sign: int, fpp_sign: int) -> int:
    zone_sign = {"non_pathology": 1, "vulnerability": 0, "pathology": -1}[zone]
    return _ZONE_OFFSET[zone_sign] + _FP_OFFSET[fp_sign] + _FPP_INDEX[fpp_sign]
