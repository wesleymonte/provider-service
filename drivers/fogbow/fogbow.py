from . import http_helper
from . import constants
import time
import enum
import uuid
import logging
import os

class ResourceState(enum.Enum):
    READY = 1
    FAILED = 2
    ERROR = 3

default_public_key_path = os.path.realpath('../keys/pp.pub')

def get_public_key():
    with open(default_public_key_path, 'r+') as file:
        return file.read()

def sync_get_compute(token, compute_id, interval, max_tries):
    tries = 0
    compute_state = http_helper.get_compute(token, compute_id).get('state')
    while(tries < max_tries and compute_state not in [ResourceState.READY.name, ResourceState.FAILED.name, ResourceState.ERROR.name]):
        time.sleep(constants.INTERVAL_CHECK_COMPUTE_STATE_SEC)
        compute_state = http_helper.get_compute(token, compute_id).get('state')
        tries += 1
    if(compute_state == ResourceState.READY.name):
        logging.info(constants.COMPUTE_REQUEST_SUCCESSFUL_MESSAGE)
    elif(compute_state == ResourceState.FAILED.name):
        raise Exception(constants.COMPUTE_REQUEST_FAILED_MESSAGE)
    elif(tries == max_tries):
        raise Exception(constants.COMPUTE_REQUEST_MAX_TRIES_MESSAGE)

def sync_get_public_ip(token, public_ip_id, interval, max_tries):
    tries = 0
    public_ip_state = http_helper.get_public_ip(token, public_ip_id).get('state')
    while(tries < max_tries and public_ip_state not in [ResourceState.READY.name, ResourceState.FAILED.name, ResourceState.ERROR.name]):
        time.sleep(constants.INTERVAL_CHECK_PUBLIC_IP_STATE_SEC)
        public_ip_state = http_helper.get_public_ip(token, public_ip_id).get('state')
        tries += 1
    if(public_ip_state == ResourceState.READY.name):
        logging.info(constants.PUBLIC_IP_REQUEST_SUCCESSFUL_MESSAGE)
    elif(public_ip_state == ResourceState.FAILED.name):
        raise Exception(constants.PUBLIC_IP_REQUEST_FAILED_MESSAGE)
    elif (public_ip_state == ResourceState.ERROR.name):
        raise Exception(constants.PUBLIC_IP_REQUEST_ERROR_MESSAGE)
    elif(tries == max_tries):
        raise Exception(constants.PUBLIC_IP_REQUEST_MAX_TRIES_MESSAGE)

def create_resource(token, compute_spec):
    compute_id = http_helper.create_compute(token, compute_spec)
    try:
        sync_get_compute(token, compute_id, constants.INTERVAL_CHECK_COMPUTE_STATE_SEC, constants.MAX_TRIES)
        public_ip_id = http_helper.create_public_ip(token, compute_id)
        sync_get_public_ip(token, public_ip_id, constants.INTERVAL_CHECK_PUBLIC_IP_STATE_SEC, constants.MAX_TRIES)
        return public_ip_id
    except Exception as e:
        http_helper.delete_public_ip(token, public_ip_id)
        time.sleep(1)
        http_helper.delete_compute(token, compute_id)
        raise e

def request_node(spec):
    spec["publicKey"] = get_public_key()
    try:
        computeSpec = http_helper.ComputeSpec.from_json(spec)
        my_token = http_helper.create_token()
        public_ip_id = create_resource(my_token, computeSpec)
        ip = http_helper.get_public_ip(my_token, resource.get('public_ip_id')).get('ip')
        return ip
    except Exception as e:
        logging.error(str(e))

def provider(node):
    ip = request_node(node.get("spec"))
    node["ip"] = ip
    #TODO Review the correct local for user field
    node["spec"]["user"] = "fogbow"
    return ip