import strawberry

from backend.api.subject.types import SubjectQuery, SubjectMutation
from backend.api.marker.types import MarkerQuery, MarkerMutation


@strawberry.type
class Query(SubjectQuery, MarkerQuery):
    pass


@strawberry.type
class Mutation(SubjectMutation, MarkerMutation):
    pass


schema = strawberry.Schema(query=Query, mutation=Mutation)
