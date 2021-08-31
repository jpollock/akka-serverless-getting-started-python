"""
Copyright 2020 Lightbend Inc.
Licensed under the Apache License, Version 2.0.
"""
import random
# imports fom Akka Serverless SDK
from akkaserverless.value_context import ValueEntityCommandContext
from akkaserverless.value_entity import ValueEntity          

# import from generated GRPC file(s)
from api_spec_pb2 import (UserProfile, MyRequest, MyResponse, _MYAPI, DESCRIPTOR as API_DESCRIPTOR)

from akkaserverless.view import View
from api_spec_pb2 import (_MYQUERYAPI, DESCRIPTOR as FILE_DESCRIPTOR)

view = View(_MYQUERYAPI,[FILE_DESCRIPTOR])

def init(entity_id: str) -> UserProfile:
    return UserProfile()

entity = ValueEntity(_MYAPI, [API_DESCRIPTOR], 'user_profiles', init)

@entity.command_handler("GetUser")
def fetch_user(state: UserProfile, command: MyRequest, context: ValueEntityCommandContext):
    return MyResponse(name= state.name, status= state.status, online= bool(random.getrandbits(1)))

@entity.command_handler("CreateUser")
def create_user(state: UserProfile, command: UserProfile, context: ValueEntityCommandContext):
    state = command
    context.update_state(state)
    return MyResponse(name= state.name, status= state.status, online= bool(random.getrandbits(1)))

@entity.command_handler("UpdateUser")
def update_user(state: UserProfile, command: UserProfile, context: ValueEntityCommandContext):
    if command.name != state.name:
        state.name = command.name
    if command.status != state.status:
        state.status = command.status

    context.update_state(state)
    return MyResponse(name= state.name, status= state.status, online= bool(random.getrandbits(1)))



