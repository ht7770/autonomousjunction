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
registryID = 'project-registry'
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
    mqtt_error_topic = 'projects/azazel-330913/topics/gatewayerrors'
    mqtt_config_topic = 'projects/azazel-330913/topics/gatewayconfig'
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

    gateway.connected = False
    if gateway.connected == False:
        print("Gateway Disconnected")
    #implement backoff
    client.connect(gateway.mqtt_bridge_hostname, gateway.mqtt_bridge_port)




def on_publish(unused_client, userdata, mid):
    print('on_publish, userdata {}, mid {}'.format(userdata, mid))
    try:
        client_addr, message = gateway.pending_responses.pop(mid)
        print('sending data over UDP {} {}'.format(client_addr, message))
        udpSerSock.sendto(message, client_addr)
        print('pending response count {}'.format(
            len(gateway.pending_responses)))
    except KeyError:
        print('Unable to find key {}'.format(mid))

def on_subscribe(unused_client, unused_userdata, mid, granted_qos):
    print('on_subscribe: mid {}, qos {}'.format(mid, granted_qos))

def on_message(unused_client, unused_userdata, message):
    """Callback when the device receives a message on a subscription."""
    payload = message.payload.decode('utf8')
    print('Received message \'{}\' on topic \'{}\' with Qos {}'.format(
        payload, message.topic, str(message.qos)))

    try:
        client_addr = gateway.subscriptions[message.topic]
        print('Relaying config[{}] to {}'.format(payload, client_addr))
        if payload == 'ON' or payload == b'ON':
            udpSerSock.sendto('ON'.encode('utf8'), client_addr)
        elif payload == 'OFF' or payload == b'OFF':
            udpSerSock.sendto('OFF'.encode('utf8'), client_addr)
        else:
            print('Unrecognized command: {}'.format(payload))
    except KeyError:
        print('Nobody subscribes to topic {}'.format(message.topic))

def createMQTT(projectID, cloudRegion, registryID, gatewayID, private_key_file, algorithm, certificateFile, mqtt_bridge_hostname, mqtt_bridge_port, JWTexpire):


    client = mqtt.Client(client_id=('projects/{}/locations/{}/registries/{}/devices/{}'.format(
            projectID,
            cloudRegion,
            registryID,
            gatewayID)))

    client.username_pw_set(username='unused', password = createJWT(projectID, algorithm, private_key_file, JWTexpire))

    client.tls_set(ca_certs=certificateFile, tls_version=ssl.PROTOCOL_TLSv1_2)

    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.on_subscribe = on_subscribe


    client.connect(mqtt_bridge_hostname, mqtt_bridge_port)

    mqtt_topic = '/devices/{}/events'.format(gatewayID)
    client.publish(mqtt_topic, 'RPI Gateway started.', qos=0)

    return client


def main():
    global gateway

    client = createMQTT(projectID, cloudRegion, registryID, gatewayID, private_key_file, algorithm, certificateFile, gateway.mqtt_bridge_hostname, gateway.mqtt_bridge_port, JWTexpire)

    while True:
        client.loop()
        print("TEST")
        if gateway.connected is False:
            print('connect status {}'.format(gateway.connected))
            time.sleep(1)
            continue

        try:
            data, client_addr = udpSerSock.recvfrom(BUFSIZE)
        except socket.error:
            continue
        print('[{}]: From Address {}:{} receive data: {}'.format(
            time.ctime(), client_addr[0], client_addr[1], data.decode("utf-8")))

        command = json.loads(data.decode('utf-8'))
        if not command:
            print('invalid json command {}'.format(data))
            continue

        action = command["action"]
        device_id = command["device"]
        template = '{{ "device": "{}", "command": "{}", "status" : "ok" }}'

        if action == 'event':
            print('Sending telemetry event for device {}'.format(device_id))
            payload = command["data"]

            mqtt_topic = '/devices/{}/events'.format(device_id)
            print('Publishing message to topic {} with payload \'{}\''.format(
                mqtt_topic, payload))
            _, event_mid = client.publish(mqtt_topic, payload, qos=0)

            message = template.format(device_id, 'event')
            udpSerSock.sendto(message.encode('utf8'), client_addr)

        elif action == 'attach':
            print('Sending telemetry event for device {}'.format(device_id))
            attach_topic = '/devices/{}/attach'.format(device_id)
            auth = ''  # TODO:    auth = command["jwt"]
            attach_payload = '{{"authorization" : "{}"}}'.format(auth)

            print('Attaching device {}'.format(device_id))
            print(attach_topic)
            response, attach_mid = client.publish(
                attach_topic, attach_payload, qos=1)

            message = template.format(device_id, 'attach')
            udpSerSock.sendto(message.encode('utf8'), client_addr)
        elif action == 'detach':
            detach_topic = '/devices/{}/detach'.format(device_id)
            print(detach_topic)

            res, mid = client.publish(detach_topic, "{}", qos=1)

            message = template.format(res, mid)
            print('sending data over UDP {} {}'.format(client_addr, message))
            udpSerSock.sendto(message.encode('utf8'), client_addr)

        elif action == "subscribe":
            print('subscribe config for {}'.format(device_id))
            subscribe_topic = '/devices/{}/config'.format(device_id)
            skip_next_sub = True

            _, mid = client.subscribe(subscribe_topic, qos=1)
            message = template.format(device_id, 'subscribe')
            gateway.subscriptions[subscribe_topic] = client_addr

            udpSerSock.sendto(message.encode('utf8'), client_addr)

        else:
            print('undefined action: {}'.format(action))

    print('Finished.')


if __name__ == '__main__':
    main()

