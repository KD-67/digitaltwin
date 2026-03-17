import strawberry


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello from the digital twin!"


schema = strawberry.Schema(query=Query)
