import graphene 
from assurance_app.schema import Query as AssuranceAppQuery, Mutation as AssuranceAppMutation

class Query (AssuranceAppQuery, graphene.ObjectType):
    pass

class Mutation(AssuranceAppMutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query = Query, mutation = Mutation)