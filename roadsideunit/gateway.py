import paho.mqtt.client as mqtt
import jwt
import json
import socket
import ssl
import os
import datetime
import time
import random
import _thread

hostIP = '192.168.1.154'
clientIP = '192.168.1.156'
port = 8888
bufferSize = 2048
address = (hostIP, port)
command = ''



# Create a UDP socket
UDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDPsocket.bind(address)
print("Socket created on port: {}".format(port))





# The initial backoff time after a disconnection occurs, in seconds.
minimum_backoff_time = 1

# The maximum backoff time before giving up, in seconds.
MAXIMUM_BACKOFF_TIME = 32

# Whether to wait with exponential backoff before publishing.
should_backoff = False

# List of required variables needed
projectID = 'azazel-330913'
cloudRegion = 'europe-west1'
registryID = 'project-registry'
deviceID = ''
gatewayID = 'roadsideunit'
certificateFile = 'roots.pem'
algorithm = 'RS256'
private_key_file = 'rsa_private.pem'
JWTexpire = 60


# Command for killing python process on RPi when socket is still in use when error occurs on program restart
# kill -9 $(ps -A | grep python | awk '{print $1}')



# Gateway class to store details about the gateway
class Gateway:

    connected = False
    mqtt_bridge_hostname = 'mqtt.googleapis.com'
    mqtt_bridge_port = 8883
    mqtt_error_topic = '/devices/{}/gatewayerrors'.format(gatewayID)
    mqtt_config_topic = '/devices/{}/gatewayconfig'.format(gatewayID)
    mqtt_command_topic = '/devices/{}/commands/#'.format(gatewayID)
    mqtt_telemetry_topic = '/devices/{}/events'.format(gatewayID)
    mqtt_state_topic = '/devices/{}/state'.format(gatewayID)

gateway = Gateway()

# Function that creates a JWT so that google cloud can authenticate the gateway and any bound devices
def createJWT(projectID, algorithm, private_key_file, JWTexpire):
    token = {
        # Time token was issued
        'iat' : datetime.datetime.utcnow(),
        # Expiry of the token
        'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=JWTexpire),
        # Audience field is set to the projectID in google cloud as per google documentation
        'aud' : projectID
    }

    # opens private key and stores in variable
    with open(private_key_file, 'r') as reader:
        privateKey = reader.read()

    # console output so we can see JWT is being created
    print('JWT being created...')
    time.sleep(0.1)
    JWT = jwt.encode(token, privateKey, algorithm=algorithm)
    print('JWT created!')
    return JWT



# Following functions handle Paho-MQTT callbacks
def error_str(rc):
    # Converts paho errors into strings
    return '{}: {}'.format(rc, mqtt.error_string(rc))



def on_connect(client, unused_userdata, unused_flags, rc):
    # Callback for when a device connects
    print('on_connect', mqtt.connack_string(rc))

    gateway.connected = True
    if gateway.connected == True:
        print("Gateway connected")

    global should_backoff
    global minimum_backoff_time
    should_backoff = False
    minimum_backoff_time = 1

    # Subscribe to the config, error and command topics.
    client.subscribe(gateway.mqtt_config_topic, qos=1)
    client.subscribe(gateway.mqtt_error_topic, qos=0)
    client.subscribe(gateway.mqtt_command_topic, qos=1)



def on_disconnect(client, unused_userdata, rc):
    # Callback for when a device disconnects
    print('on_disconnect', error_str(rc))
    gateway.connected = False
    if gateway.connected == False:
        print("Gateway Disconnected")
    #implement backoff
    client.connect(gateway.mqtt_bridge_hostname, gateway.mqtt_bridge_port)




def on_publish(unused_client, userdata, mid):
    print('on_publish, userdata {}, mid {}'.format(userdata, mid))



def on_subscribe(unused_client, unused_userdata, mid, granted_qos):
    print('on_subscribe: mid {}, qos {}'.format(mid, granted_qos))


def on_message(unused_client, unused_userdata, message):
    payload = str(message.payload.decode("utf-8"))
    print(
        "Received message '{}' on topic '{}' with Qos {}".format(
            payload, message.topic, str(message.qos)
        )
    )

# Function that creates the MQTT client
def createMQTT(projectID, cloudRegion, registryID, gatewayID, private_key_file, algorithm, certificateFile, mqtt_bridge_hostname, mqtt_bridge_port, JWTexpire):

    client = mqtt.Client(client_id=('projects/{}/locations/{}/registries/{}/devices/{}'.format(projectID, cloudRegion, registryID, gatewayID)))

    # Google cloud only takes values in the password field
    client.username_pw_set(username='unused', password=createJWT(projectID, algorithm, private_key_file, JWTexpire))
    # Enable SSl/TLS
    client.tls_set(ca_certs=certificateFile, tls_version=ssl.PROTOCOL_TLSv1_2)

    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.on_subscribe = on_subscribe

    # Connect to MQTT bridge using google hostname and recommended port
    client.connect(mqtt_bridge_hostname, mqtt_bridge_port)


    client.publish(gateway.mqtt_state_topic, 'Roadside Unit Started', qos=0)
    return client

# UPD function that is used by the other thread, listens for messages on the UDP socket
def UDPlistener():
    global command
    while True:
        data, clientMessage = UDPsocket.recvfrom(bufferSize)
        command = json.loads(data.decode("utf-8"))








def main():
    global gateway
    global command

    # duration gateway is active for in seconds
    duration = 1000

    oldMessage = ''

    # creating the client using variables provided at start of code
    client = createMQTT(projectID, cloudRegion, registryID, gatewayID, private_key_file, algorithm, certificateFile, gateway.mqtt_bridge_hostname, gateway.mqtt_bridge_port, JWTexpire)

    # Using multi threading so that the UDP can listen for messages in background while main is running
    _thread.start_new_thread(UDPlistener, ())
    print("Starting UDP listener...")

    # loop through the duration to keep the gateway running
    for i in range(1, duration):
        client.loop()

        # Sends an update about the gateway state to google cloud every 10 seconds
        if (i % 10 == 0) and (gateway.connected == True):
            client.publish(gateway.mqtt_state_topic, "Roadside Unit Active", qos=0)
        if should_backoff:
            if minimum_backoff_time > MAXIMUM_BACKOFF_TIME:
                print("Exceeded max backoff time")
                break

            delay = minimum_backoff_time + random.randint(0, 1000) / 1000.0
            time.sleep(delay)
            minimum_backoff_time *= 2
            client.connect(gateway.mqtt_bridge_hostname, gateway.mqtt_bridge_port)


        if command == '' or command == oldMessage:
            continue
        elif command['action'] == 'subscribe':
            deviceConfig = '/devices/{}/config'.format(command['device'])
            client.subscribe(deviceConfig, qos=1)
            oldMessage = command
        elif command['action'] == 'event':
            deviceTopic = '/devices/{}/state'.format(command['device'])
            client.publish(deviceTopic, command['data'], qos=0)
            oldMessage = command
        elif command['action'] == 'attach':
            attach_topic = '/devices/{}/attach'.format(command['device'])
            mqtt_topic = '/devices/{}/devicetelem'.format(command['device'])
            auth = ''
            attach_payload = '{{"authorization" : "{}"}}'.format(auth)
            client.publish(attach_topic, attach_payload, qos=1)
            client.subscribe(mqtt_topic, qos=1)
            client.publish(mqtt_topic, command['data'], qos=0)
            oldMessage = command



        else:
            print("Undefined action!")












if __name__ == '__main__':
    main()

