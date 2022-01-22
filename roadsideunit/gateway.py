from __future__ import print_function
import paho.mqtt.client as mqtt
import jwt
import json
import socket
import ssl
import os
import argparse
import datetime
import time


HOST = ''
PORT = 10000
BUFSIZE = 2048
ADDR = (HOST, PORT)

udpSerSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udpSerSock.setblocking(False)
udpSerSock.bind(ADDR)


projectID = 'azazel-330913'
cloudRegion = 'europe-west1'
registryID = 'azazel-devices'
deviceID = ''
gatewayID = 'roadsideunit'
certificateFile = 'roots.pem'
algorithm = 'RS256'
private_key_file = 'rsa_private.pem'
JWTexpire = 60





class Gateway:

    connected = False
    mqtt_bridge_hostname = 'mqtt.googleapis.com'
    mqtt_bridge_port = 8883
    mqtt_error_topic = ''
    mqtt_config_topic = ''
    pending_responses = {}
    pending_subscribes = {}
    subscriptions = {}

gateway = Gateway()

def createJWT(projectID, algorithm, private_key_file, JWTexpire):

    token = {
        'iat' : datetime.datetime.utcnow(),
        'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=JWTexpire),
        'aud' : projectID
    }

    with open(private_key_file, 'r') as reader:
        privateKey = reader.read()

    print('JWT being created')

    return jwt.encode(token, privateKey, algorithm=algorithm)

def error_str(rc):
    return '{}: {}'.format(rc, mqtt.error_string(rc))

def on_connect(client, unused_userdata, unused_flags, rc):
    """Callback for when a device connects."""
    print('on_connect', mqtt.connack_string(rc))

    gateway.connected = True
    if gateway.connected == True:
        print("Gateway connected")

    # Subscribe to the config and error topics.
    client.subscribe(gateway.mqtt_config_topic, qos=1)
    client.subscribe(gateway.mqtt_error_topic, qos=0)

def on_disconnect(client, unused_userdata, rc):
    """Paho callback for when a device disconnects."""
    print('on_disconnect', error_str(rc))
    gateway.connected = False
    #implement backoff
    client.connect(
        gateway.mqtt_bridge_hostname, gateway.mqtt_bridge_port)


def createMQTT(projectID, cloudRegion, registryID, gatewayID, private_key_file, algorithm, certificateFile, mqtt_bridge_hostname, mqtt_bridge_port, JWTexpire):


    client = mqtt.Client(client_id=('projects/{}/locations/{}/registries/{}/devices/{}'.format(
            projectID,
            cloudRegion,
            registryID,
            gatewayID)))

    client.username_pw_set(username='unused', password = createJWT(projectID, algorithm, private_key_file, JWTexpire)

    client.tls_set(ca_certs=certificateFile, tls_version=ssl.PROTOCOL_TLSv1_2)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    client.connect(mqtt_bridge_hostname, mqtt_bridge_port)

    mqtt_topic = '/devices/{}/events'.format(gatewayID)
    client.publish(mqtt_topic, 'RPI Gateway started.', qos=0)

    return client


def main():
    global gateway

    client = createMQTT(projectID, cloudRegion, registryID, gatewayID, private_key_file, algorithm, certificateFile, gateway.mqtt_bridge_hostname, gateway.mqtt_bridge_port, JWTexpire)

    client.loop()
    if gateway.connected is False:
        print('connect status {}'.format(gateway.connected))
        time.sleep(1)

if __name__ == '__main__':
    main()

