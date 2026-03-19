# Converts a list of raw data point dicts into the numeric arrays the polynomial
# fitter expects. Time is expressed as elapsed hours since the first reading so
# that the polynomial operates on a human-readable scale. Raw values are
# normalized to health scores so that all markers share the same [-inf, 1] axis.

from datetime import datetime

from .compute_normalization_params import compute_normalization_params
from .normalize import normalize


def build_time_and_health_arrays(
    data_points: list[dict],
    zone_boundaries: dict,
) -> tuple[list[float], list[float], datetime]:
    params = compute_normalization_params(zone_boundaries)
    mid = params["mid"]
    half_range = params["half_range"]

    t0: datetime = data_points[0]["parsed_timestamp"]

    x_hours: list[float] = [
        (dp["parsed_timestamp"] - t0).total_seconds() / 3600.0
        for dp in data_points
    ]
    h_values: list[float] = [
        normalize(dp["value"], mid, half_range)
        for dp in data_points
    ]

    return x_hours, h_values, t0
