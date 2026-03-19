# Collapses a continuous derivative value into one of three directional classes:
# improving (+1), stable (0), or worsening (-1). A small dead-band around zero
# prevents noisy near-flat slopes from flickering between improving and worsening.

DERIVATIVE_ZERO_THRESHOLD = 0.001


def sign_class(value: float) -> int:
    if value > DERIVATIVE_ZERO_THRESHOLD:
        return 1
    if value < -DERIVATIVE_ZERO_THRESHOLD:
        return -1
    return 0
