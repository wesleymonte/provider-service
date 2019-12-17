from . import http_helper
from . import constants
import time
import enum
import uuid
import logging

class ResourceState(enum.Enum):
    READY = 1
    FAILED = 2
    ERROR = 3

def sync_get_compute(token, compute_id, interval, max_tries):
    tries = 0
    compute_state = http_helper.get_compute(token, compute_id).get('state')
    while(tries < max_tries and compute_state not in [ResourceState.READY.name, ResourceState.FAILED.name, ResourceState.ERROR.name]):
        time.sleep(constants.INTERVAL_CHECK_COMPUTE_STATE_SEC)
        compute_state = http_helper.get_compute(token, compute_id).get('state')
        tries += 1
    if(compute_state == ResourceState.READY.name):
        return (True, constants.COMPUTE_REQUEST_SUCCESSFUL_MESSAGE)
    elif(compute_state == ResourceState.FAILED.name):
        return (False, constants.COMPUTE_REQUEST_FAILED_MESSAGE)
    elif(tries == max_tries):
        return (False, constants.COMPUTE_REQUEST_MAX_TRIES_MESSAGE)
    return (False, "Runtime Error")

def sync_get_public_ip(token, public_ip_id, interval, max_tries):
    tries = 0
    public_ip_state = http_helper.get_public_ip(token, public_ip_id).get('state')
    while(tries < max_tries and public_ip_state not in [ResourceState.READY.name, ResourceState.FAILED.name, ResourceState.ERROR.name]):
        time.sleep(constants.INTERVAL_CHECK_PUBLIC_IP_STATE_SEC)
        public_ip_state = http_helper.get_public_ip(token, public_ip_id).get('state')
        tries += 1
    if(public_ip_state == ResourceState.READY.name):
        return (True, constants.PUBLIC_IP_REQUEST_SUCCESSFUL_MESSAGE)
    elif(public_ip_state == ResourceState.FAILED.name):
        return (False, constants.PUBLIC_IP_REQUEST_FAILED_MESSAGE)
    elif (public_ip_state == ResourceState.ERROR.name):
        return (False, constants.PUBLIC_IP_REQUEST_FAILED_MESSAGE)
    elif(tries == max_tries):
        return (False, constants.PUBLIC_IP_REQUEST_MAX_TRIES_MESSAGE)

def create_resource(token, compute_spec):
    compute_id = http_helper.create_compute(token, compute_spec)
    result, message = sync_get_compute(token, compute_id, constants.INTERVAL_CHECK_COMPUTE_STATE_SEC, constants.MAX_TRIES)
    logging.info(message)
    if result:
        public_ip_id = http_helper.create_public_ip(token, compute_id)
        result, message = sync_get_public_ip(token, public_ip_id, constants.INTERVAL_CHECK_PUBLIC_IP_STATE_SEC, constants.MAX_TRIES)
        logging.info(message)
        if result:
            resource = {'compute_id':compute_id, 'public_ip_id':public_ip_id}
            return resource, "Successful resource create"
        else:
            http_helper.delete_public_ip(token, public_ip_id)
            time.sleep(1)
            http_helper.delete_compute(token, compute_id)
            return None, message
    else:
        http_helper.delete_compute(token, compute_id)
        return None, message

def request_node(spec):
    computeSpec = http_helper.ComputeSpec.from_json(spec)
    my_token = http_helper.create_token()
    resource, message = create_resource(my_token, computeSpec)
    if resource is None:
        logging.error("Error while requesting fogbow resource: " + message)
        return None
    else:
        ip = http_helper.get_public_ip(my_token, resource.get('public_ip_id')).get('ip')
        print("Got node from fogbow: " + ip)
        return ip