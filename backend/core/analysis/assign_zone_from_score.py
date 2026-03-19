# Maps a health score to one of three clinical zones.
# Scores comfortably above zero are non-pathological, scores near zero sit in
# the vulnerability band where the marker is at the edge of the healthy range,
# and negative scores indicate pathology outside that range entirely.


def assign_zone_from_score(h: float, vulnerability_margin: float) -> str:
    if h > vulnerability_margin:
        return "non_pathology"
    if h < -vulnerability_margin:
        return "pathology"
    return "vulnerability"
