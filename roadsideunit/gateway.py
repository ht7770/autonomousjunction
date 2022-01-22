import paho.mqtt.client as mqtt
import jwt
import json
import socket
import ssl
import os
import argparse
import datetime
import time



projectID = 'azazel-330913'
cloudRegion = 'europe-west1'
registryID = 'azazel-devices'
deviceID = ''
gatewayID = 'roadsideunit'
certificateFile = ''
algorithm = 'RS256'
private_key_file = ''
JWTexpire = 60

gatewayConnected = False

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




def createMQTT(projectID, cloudRegion, registryID, gatewayID, private_key_file,
        algorithm, certificateFile, mqtt_bridge_hostname, mqtt_bridge_port,
        JWTexpire):


    client = mqtt.Client(client_id=('projects/{}/locations/{}/registries/{}/devices/{}'.format(
            project_id,
            cloud_region,
            registry_id,
            gateway_id))))

    client.username_pw_set(
        username='unused',
        password = createJWT(projectID, algorithm, private_key_file, JWTexpire)
    )

    client.tls_set(ca_certs=certificateFile, tls_version=ssl.PROTOCOL_TLSv1_2)
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.on_subscribe = on_subscribe

    client.connect(mqtt_bridge_hostname, mqtt_bridge_port)

    mqtt_topic = '/devices/{}/events'.format(gateway_id)
    client.publish(mqtt_topic, 'RPI Gateway started.', qos=0)

    return client



