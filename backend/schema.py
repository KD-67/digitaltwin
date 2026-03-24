import strawberry

from backend.api.subject.types import SubjectQuery, SubjectMutation
from backend.api.marker.types import MarkerQuery, MarkerMutation
from backend.api.measurement.types import MeasurementQuery, MeasurementMutation
from backend.api.analysis.types import AnalysisQuery


@strawberry.type
class Query(SubjectQuery, MarkerQuery, MeasurementQuery, AnalysisQuery):
    pass


@strawberry.type
class Mutation(SubjectMutation, MarkerMutation, MeasurementMutation):
    pass


schema = strawberry.Schema(query=Query, mutation=Mutation)
