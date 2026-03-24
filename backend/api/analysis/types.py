import strawberry
from typing import List

from backend.core.analysis.normalize import normalize
from backend.core.analysis.compute_normalization_params import compute_normalization_params


@strawberry.input
class RawMeasurementInput:
    marker_id: str
    measured_at: str
    value: str


@strawberry.type
class NormalizedMeasurement:
    marker_id: str
    measured_at: str
    value: str
    h_score: float


@strawberry.type
class AnalysisQuery:
    @strawberry.field
    def normalize_health_scores(
        self,
        measurements: List[RawMeasurementInput],
        healthy_min: float,
        healthy_max: float,
    ) -> List[NormalizedMeasurement]:
        params = compute_normalization_params({"healthy_min": healthy_min, "healthy_max": healthy_max})
        mid = params["mid"]
        half_range = params["half_range"]
        return [
            NormalizedMeasurement(
                marker_id=m.marker_id,
                measured_at=m.measured_at,
                value=m.value,
                h_score=normalize(float(m.value), mid, half_range),
            )
            for m in measurements
        ]
