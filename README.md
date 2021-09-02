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

from akkaserverless.action_context import ActionContext
from akkaserverless.action_protocol_entity import Actio
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
        16. **add query**
        17. Open up proto file
            1. First, we have to know that Akka Serverless users (CQRS)][https://martinfowler.com/bliki/CQRS.html] for supporting querying capabilities; the query mechanism always resides in a separate service/API, even if running within the same container environment. This ultimately gives the developer more control and performance for querying, whether for basic or more advanced needs. THis means that we need to add a peer service definition. Normally, we're likely to do this in a separate file and probably repository as well. But for now we'll do in the same API specification file: `api_spec.proto`.
                1. Add an empty service definition at the end of the file, called `MyQueryApi`:
                    ```
                    service MyQueryApi {

                    }
                    ```
                2. Querying in Akka Serverless is based on a feature called (`views`)[https://developer.lightbend.com/docs/akka-serverless/reference/glossary.html#view]. Views are created automatically by Akka Serverless based on the **events** that occur, e.g. new data created, updated or deleted. As such, we have to define an API - not called directly by a develope - that will be used by Akka Serverless to connect the events to the query tables that will be created and managed. We do this 

                    ```
                    rpc UpdateView(UserProfile) returns (UserProfile) {
                        option (akkaserverless.method).eventing = {
                        in: {
                            value_entity: "user_profiles"
                        }
                        };
                        option (akkaserverless.method).view.update = {
                        table: "user_profiles"
                        };
                    }


                    ```
                3. The second part of our new `MyQueryApi` will be the actual API call that can be used by a developer to make the actual query. In this case, let's do a simple query for fetching all of the users created by our `MyApi`. Name of the API is `GetUsers`, with no input parameters supported an a resonse of type `UsersResponse`. The annotation used, to define the query, is `option (akkaserverless.method).view.query` and the query is a simple select statement: `SELECT * AS results FROM user_profiles`.

                   ```
                    rpc GetUsers(google.protobuf.Empty) returns (UsersResponse) {
                        option (akkaserverless.method).view.query = {
                        query: "SELECT * AS results FROM user_profiles"
                        };
                        option (google.api.http) = {
                            get: "/users"
                        };  
                    }  
                   ```
                4. In the above, we have a new message type that we have to define: `UsersResponse`. In this case, it is a simple list of `UserProfile` messages. The definition is:
                    ```
                    message UsersResponse {
                        repeated UserProfile results = 1; 
                    }
                    ```
                5. Now we have our API defined and the eventing setup so the underlying data structures are populated. We connect this to code by updating our `api_impl.py`. We need to import some modules and then setup the View. You can add the below right after the `from api_spec_pb2 import (UserProfile, MyRequest, MyResponse, _MYAPI, DESCRIPTOR as API_DESCRIPTOR)` line. You could also put at the bottom of the file as well.
                    ```
                    from akkaserverless.view import View
                    from api_spec_pb2 import (_MYQUERYAPI, DESCRIPTOR as FILE_DESCRIPTOR)

                    view = View(_MYQUERYAPI,[FILE_DESCRIPTOR])
                    ```
                6. The final step is to expose it to the Akka Serverless run-time. Update the `api_service.py` file to import the `view` and add it to the list of components served. The file should look like:

                    ```
                    """
                    Copyright 2020 Lightbend Inc.
                    Licensed under the Apache License, Version 2.0.
                    """

                    from akkaserverless.akkaserverless_service import AkkaServerlessService
                    from api_impl import entity as myapi
                    from api_impl import view as myquery
                    import logging

                    if __name__ == '__main__':
                        logging.basicConfig(level=logging.DEBUG)
                        
                        # create service and add components
                        service = AkkaServerlessService()
                        service.add_component(myapi)
                        service.add_component(myquery)
                        service.start()


                    ```
                7. Start
                8. `curl -X POST -H "Content-Type: application/json" http://localhost:9000/users -d '{"user_profile_id": "test", "name": "My Name", "status": "active", "devices":[]}'`
                9. `curl -X GET -H "Content-Type: application/json" http://localhost:9000/users`

# Implement Update A User's devices via Pubsub (Eventing)

1. Open the `api_spec.proto` to add a new API method to the `MyApi` service. 
   ```
    rpc UpdateUserDevices(UserProfile) returns (google.protobuf.Empty) {
        option (akkaserverless.method).eventing = {
            in: {
              topic: "device_added"
            }
        };
    };  
    ```
2. At the bottom of the `api_spec.proto`, add a new service that will simulate external system.
    ```
    message UserDevices {
        string user_profile_id = 1;
        repeated Device devices = 4;
    
    }

    service MyEventApi {
        rpc ValidateDevices(UserDevices) returns (UserProfile) {
            option (akkaserverless.method).eventing = {
                out: {
                topic: "device_added"
                }
            };
            option (google.api.http) = {
                post: "/users/{user_profile_id}/devices",
                body: "*"
            };
        };             
    }
    ```
3. 