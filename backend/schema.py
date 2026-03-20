import strawberry

from backend.api.subject.types import SubjectQuery, SubjectMutation
from backend.api.marker.types import MarkerQuery, MarkerMutation
from backend.api.measurement.types import MeasurementQuery, MeasurementMutation


@strawberry.type
class Query(SubjectQuery, MarkerQuery, MeasurementQuery):
    pass


@strawberry.type
class Mutation(SubjectMutation, MarkerMutation, MeasurementMutation):
    pass


schema = strawberry.Schema(query=Query, mutation=Mutation)
