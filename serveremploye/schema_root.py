import graphene 
from employe_app.schema import Query as EmployeAppQuery, Mutation as EmployeAppMutation

class Query (EmployeAppQuery, graphene.ObjectType):
    pass

class Mutation(EmployeAppMutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query = Query, mutation = Mutation)