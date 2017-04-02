"""Publish MQTT from json input

This module takes a json 'body' from input (intended to be used as a lambda handler)
and publishes the content to an MQTT broker.
"""

import os
import urlparse
import json
from ssl import PROTOCOL_TLSv1
import paho.mqtt.publish as publish

def parse_str_as_boolean(boolean):
    """Helper to return boolean from string"""
    return boolean.lower() in "true"

def handler(event, _context):
    """Return json response after publishing payload to mqtt broker"""
    # host, ssl based on env
    url = urlparse.urlparse(os.environ.get('MQTT_URL'))

    # check for secure scheme
    tls = None
    if url.scheme == 'mqtts':
        tls = {'ca_certs': './cacert.pem', 'tls_version': PROTOCOL_TLSv1}

    default_parameters = {
        'username': url.username,
        'password': url.password,
        'topic': 'test_topic',
        'payload': 'test_payload',
        'retain': 'false',
        'qos': 2
    }

    parameters = default_parameters.copy()
    parameters.update(json.loads(event['body']))

    auth = {'username': parameters['username'], 'password': parameters['password']}

    publish.single(
        topic=parameters['topic'],
        payload=parameters['payload'],
        qos=parameters['qos'],
        retain=parse_str_as_boolean(parameters['retain']),
        hostname=url.hostname,
        port=url.port,
        auth=auth,
        tls=tls
    )

    response = {
        "statusCode": 200,
        "body": json.dumps({'message':'delivered'})
    }

    return response
