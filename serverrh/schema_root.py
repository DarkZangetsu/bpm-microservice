import graphene 
from rh_app.schema import Query as RhAppQuery, Mutation as RhAppMutation

class Query (RhAppQuery, graphene.ObjectType):
    pass

class Mutation(RhAppMutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query = Query, mutation = Mutation)