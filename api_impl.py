"""
Copyright 2020 Lightbend Inc.
Licensed under the Apache License, Version 2.0.
"""
import random
# imports fom Akka Serverless SDK
from akkaserverless.action_context import ActionContext
from akkaserverless.action_protocol_entity import Action

# import from generated GRPC file(s)
from api_spec_pb2 import (MyRequest, MyResponse, _MYAPI, DESCRIPTOR as API_DESCRIPTOR)


entity = Action(_MYAPI, [API_DESCRIPTOR])

@entity.unary_handler("GetUser")
def fetch_user(command: MyRequest, context: ActionContext):
    resp = MyResponse(name= "My Name", status= random.choice(['active', 'inactive']), online= bool(random.getrandbits(1)))
    return resp