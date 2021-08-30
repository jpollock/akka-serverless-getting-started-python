Sign-up, CLI, Docker

Assumes:

Python3, Docker


1. See what's there
    1. `git clone`
    2. cd dir
    3. docker-compose up -d
    4. `curl -X POST -H "Content-Type: application/json" http://localhost:9000/hello -d '{"name": "My Name"}'`

    ```
    {"text":"Do you want to play a game, My Name?"}
    ```

2. Setup for developing
    1. Sign-up, CLI
    2. virtual env: python3 -m venv myenv
    3. load env: `source myenv/bin/activate`
    4. `pip install -r requirements.txt`
    5. `docker-compose -f docker-compose-proxy.yml up -d`
    5. ./bin/start.sh
    6. `curl -X POST -H "Content-Type: application/json" http://localhost:9000/hello -d '{"name": "My Name"}'`

We're here to build something. Running the above was interesting, just to get a sense of what some aspects of the developer experience are:

1. To run fully in local environment, running the Akka Serverless sidecar proxy will be critical; this was the `docker-compose -f docker-compose-proxy.yml up -d` above;
2. 

For a system that is managing User Profiles that need to be directly incorporated into a run-time application, e.g. tracking last watched movies for a streaming video service User Profile or currently connected devices for a customer support User Profile. The objective of this exercise will be to deliver on the following requirements:


1. We want to fetch a User Profile given the identifier for a particular user using a standard API approach.

# Design the Fetch User Profile API

1. Define the api
    1. open the `api_spec.proto` file
    2. Goal is to make this a simple API that receives requests - in this case a GET of User Profile data with a result of some data.
    3. Let's focus on the request:
        1. The data sent to the API, in this case, is quite simple: a `name`. This data will either be part of a JSON payload or part of the URI or request parameters. Fetching User Profile data by a person's name wouldn't work n the real world - too many Jeremys out there! - so let's change name to be a parameter more like an `id`. Let's change `name` to `user_profile_id`. 
            ```
            message MyRequest {
               string user_profile_id = 1;
            }
            ```
    4. Now let's move on to what data we expect to send back as a response to this request for User Profile data. `text` seems to not be a great choice so let's change that to `name` (which nows seems appropiate!). And a `name` for a User Profile is rather bare bones so we will add some other attributes of a User Profile that we would like to see. 
        1. Change `text` to `name`.
        2. Add `string status = 2` on the line below.
        3. Add `bool online = 3` on the next line.

        Your `MyResponse` should look like the below. Note that the numbers (`1`,`2`,`3`) indicate position in the returned response; the order of things matter.
        ```
        message MyResponse {
           string name = 1;
           string status = 2;
           bool online = 3;
        }
        ```
    5. We have a request and a response. Now we need the API! The starter code in the file is for a `POST /hello` API call. We need to make some changes.
        1. Change `Hello` to `GetUser`. We'll use this identifier in the actual code that we write to implement the API logic.
        2. Change `post` to `get` since this is a fetch of data.
        3. Remove the `body: "*"` line.
        3. Change `/hello` to `/users/{user_profile_id}`; we're putting the parameter, `user_profile_id`, from our `MyRequest` message directly into the URI path.
        
        Finished API specification should look like:

        ```
        // boilerplate for a new action API
        syntax = "proto3";

        import "akkaserverless/annotations.proto";
        import "google/api/annotations.proto";


        message MyRequest {
            string user_profile_id = 1;
        }

        message MyResponse {
            string name = 1;
            string status = 2;
            bool online = 3;
        }

        service ThingActionService {
            rpc Users(MyRequest) returns (MyResponse) {
                option (google.api.http) = {
                    get: "/users/{user_profile_id}",
                    body: "*"
                };  
            }
        }
        ```

3. Generate code by running, from terminal window, in the project directory: `./bin/compile.sh`.
4. Open the `api_impl.py` so that we can add our business logic.
5. Change `@action.unary_handler("Hello")` to `@action.unary_handler("GetUser")`. This essentially performs the routing logic, to map the incoming API request to the URI path specified in the `api_spec.proto` to the function that will handle the request.
6. Change `def hello` to `def fetch_user`. This is not necessary since we already have the routing done through the above change but it makes our code more sensible to the reader.
7. At the top of the file, right before `# imports fom Akka Serverless SDK` add a new line: `import random`. We will just use some random data for fun.
8. In the now named `users` function, change the line, `resp = MyResponse(text= "Do you want to play a game, " + command.name + "?")` to `resp = MyResponse(name= "My Name", status= random.choice(['active', 'inactive']), online= bool(random.getrandbits(1)))`

```
"""
Copyright 2020 Lightbend Inc.
Licensed under the Apache License, Version 2.0.
"""

from dataclasses import dataclass, field
from typing import MutableSet
import random

from google.protobuf.empty_pb2 import Empty

from akkaserverless.context import ActionContext
from akkaserverless.protocol_entity import Action
from api_spec_pb2 import (MyRequest, MyResponse, _THINGACTIONSERVICE, DESCRIPTOR as API_DESCRIPTOR)


action = Action(_THINGACTIONSERVICE, [API_DESCRIPTOR])

@action.unary_handler("Hello")
def hello(command: MyRequest, context: ActionContext):
    resp = MyResponse(name= "My Name", status= random.choice(['active', 'inactive']), online= bool(random.getrandbits(1)))
    return resp
```
9. ./bin/start.sh
10. `curl -X GET -H "Content-Type: application/json" http://localhost:9000/users/$\{uuidgen\}` should return

```
{"name":"My Name","status":"active","online":false}%  
```
`status` and `online` values should change randomly as you run that curl command repeatedly.


# Design the Create/Update User Profile API

So far we have built a simple API and one that has not stored any data or retrieved any either, from a database or elsewhere.

> For a system that is managing User Profiles that need to be directly incorporated into a run-time application, e.g. tracking last watched movies for a streaming video service User Profile or currently connected devices for a customer support User Profile.

The objective of this exercise will be to deliver on the following requirements:

1. We want to create and update a User Profile using a standard API approach.

1. Define the api
    1. open the `api_spec.proto` file
        1. Add a new message request, to capture the information we want to pass into the API: name of the User, status of the User, e.g. a customer or not, and list of devices.
            ```
            message UserProfile {
                string user_profile_id = 1;
                string name = 2;
                string status = 3;
                repeated Device devices = 4;
            }

            message Device {
                string id = 1;
                string name = 2;
            }
            ```
        2. Annotate the `user_profile_id` parameter in both the `UserProfile` and `MyRequest` messages such that the parameter, `user_profile_id`, is denoted as the identifier that Akka Serverless should use for Value Entity (KV) storage and manipulation. The annotation is: `[(akkaserverless.field).entity_key = true]`. See below for example on where to put.
        
        ```

        message UserProfile {
            string user_profile_id = 1 [(akkaserverless.field).entity_key = true];
            string name = 2;
            string status = 3;
            repeated Device devices = 4;
        }

        message Device {
            string id = 1;
            string name = 2;
        }

        message MyRequest {
            string user_profile_id = 1 [(akkaserverless.field).entity_key = true];
        }
        ```

        3. Update the `MyResponse` so that it can be used in this new API as well; we are just adding additional data parameters that we will include in the body of the response.
            ```
            message MyResponse {
                string name = 1;
                string status = 2;
                bool online = 3;
                repeated Device devices = 4;
            }
            ```
        4. Add the API itself. We'll two: a `POST /users` for creation of a UserProfle and `PUT /users/{user_profile_id}` for the update.

            ```
            service MyApi {
                rpc GetUser(MyRequest) returns (MyResponse) {
                    option (google.api.http) = {
                        get: "/users/{user_profile_id}",
                    };  
                }
                rpc CreateUser(UserProfile) returns (MyResponse) {
                    option (google.api.http) = {
                        post: "/users",
                        body: "*"
                    };  
                }
                rpc UpdateUser(UserProfile) returns (MyResponse) {
                    option (google.api.http) = {
                        put: "/users/{user_profile_id}",
                        body: "*"
                    };  
                }

            }
            ```

        5. Generate code by running, from terminal window, in the project directory: `./bin/compile.sh`.
        6. Open the `api_impl.py` so that we can add our business logic. First, change the implementation of our API from an Action to a Value Entity. Replace:
          ```
          from akkaserverless.action_context import ActionContext
          from akkaserverless.action_protocol_entity import Action
          ```
          with
          ```
          from akkaserverless.value_context import ValueEntityCommandContext
          from akkaserverless.value_entity import ValueEntity          
          ```
        7. Add `UserProfile` in front of `MyRequest` in the import statement:
            `from api_spec_pb2 import (UserProfile, MyRequest, MyResponse, _MYAPI, DESCRIPTOR as API_DESCRIPTOR)`.
        8. Change the API implementation type from `Action` to `ValueEntity`. This is done in this line: `entity = Action(_MYAPI, [API_DESCRIPTOR])`. The new code should be `entity = ValueEntity(_MYAPI, [API_DESCRIPTOR])`.
        9. 10. Add init, add entity type
        8. Since we've moved from `Action` to `ValueEntity` we need to change some things in our `GetUser` API code. 
            1. Change `unary_handler` to `command_handler`.
            2. Change `command: MyRequest, context: ActionContext` to `state: UserProfile, command: MyRequest, context: ValueEntityCommandContext`.
            3. The api specification calls for a response of type `MyResponse`.Change 
                ```
                resp = MyResponse(name= "My Name", status= random.choice(['active', 'inactive']), online= bool(random.getrandbits(1)))
                return resp
                ```
                to
                ```
                resp = MyResponse(name= state.name, status= state.status, online= bool(random.getrandbits(1)))
                return resp
                ```
        9. Add a new command handler for `CreateUser`.
            1. Add a new line after the `fetch_user` function: `@entity.command_handler("CreateUser")`.
            2. Define a function, called `create_user` with parameters of `state`, `command`, `context`. **The Akka Serverless Python SDK depends on these exact names**.
            3. Your code should look like:
            ```
            @entity.command_handler("CreateUser")
            def create_user(state: UserProfile, command: UserProfile, context: ValueEntityCommandContext):
                state = command
                context.update_state(state)
                return MyResponse(name= state.name, status= state.status, online= bool(random.getrandbits(1))ß)
            ```
        11. Start
        12. `curl -X POST -H "Content-Type: application/json" http://localhost:9000/users -d '{"user_profile_id": "test", "name": "My Name", "status": "active", "devices":[]}'`
        13. `curl -X GET -H "Content-Type: application/json" http://localhost:9000/users/test`
        14. Add a new command handler for `UpdateUser`.
            1. Add a new line after the `create_user` function: `@entity.command_handler("UpdateUser")`.
            2. Define a function, called `update_user` with parameters of `state`, `command`, `context`.  
           3. Let's make it a bit more complex and do some basic testing. The idea is the same: select which data off of the command (request) that you want to map into the state.
           ```
            @entity.command_handler("UpdateUser")
            def update_user(state: UserProfile, command: UserProfile, context: ValueEntityCommandContext):
                if command.name != state.name:
                    state.name = command.name
                if command.status != state.status:
                    state.status = command.status

                context.update_state(state)
                return MyResponse(name= state.name, status= state.status, online= bool(random.getrandbits(1)))
            ```
        15. Start
