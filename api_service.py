"""
Copyright 2020 Lightbend Inc.
Licensed under the Apache License, Version 2.0.
"""

from akkaserverless.akkaserverless_service import AkkaServerlessService
from api_impl import entity as myapi
from api_impl import view as myquery
from api_impl import action as myevent
import logging

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    
    # create service and add components
    service = AkkaServerlessService()
    service.add_component(myapi)
    service.add_component(myquery)
    service.add_component(myevent)
    service.start()
