import base64
import io
import os
import sys
import time
import random

from google.api_core.exceptions import AlreadyExists
from google.cloud import iot_v1
from google.cloud import pubsub
from google.oauth2 import service_account

def hello_pubsub(event, context):
     direction = base64.b64decode(event['data']).decode('utf-8')
     projectID = 'azazel-330913'
     cloudRegion = 'europe-west1'
     registryID = 'project-registry'
     deviceID = 'car1'

     possibleCommands = ["AUTHORISED", "UNAUTHORISED"]

     print("Sending command to device")
     client = iot_v1.DeviceManagerClient()
     device_path = client.device_path(projectID, cloudRegion, registryID, deviceID)

     command = random.choice(possibleCommands)
     print("Sending command to device: {}".format(command))
     data = command.encode("utf-8")

     if command == "UNAUTHORISED":
          client.send_command_to_device(request={"name": device_path, "binary_data": data})
          time.sleep(5)
          newCommand = "AUTHORISED"
          data = newCommand.encode("utf-8")
          return client.send_command_to_device(request={"name": device_path, "binary_data": data})
     else:
          return client.send_command_to_device(request={"name": device_path, "binary_data": data})

     
