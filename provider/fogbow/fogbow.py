import http_helper
import constants
import time

def sync_get_compute(token, compute_id, interval, max_tries):
    tries = 0
    compute_state = http_helper.get_compute(token, compute_id)['state']
    while(tries < max_tries and compute_state != "READY" and compute_state != "FAILED"):
        time.sleep(constants.INTERVAL_CHECK_COMPUTE_STATE_SEC)
        compute_state = http_helper.get_compute(token, compute_id)['state']
        tries += 1
    if(compute_state == "READY"):
        return (True, constants.COMPUTE_REQUEST_SUCCESSFUL_MESSAGE)
    elif(compute_state == "FAILED"):
        return (False, constants.COMPUTE_REQUEST_FAILED_MESSAGE)
    elif(tries == max_tries):
        return (False, constants.COMPUTE_REQUEST_MAX_TRIES_MESSAGE)
    return (False, "Runtime Error")

def sync_get_public_ip(token, public_ip_id, interval, max_tries):
    tries = 0
    public_ip_state = http_helper.get_public_ip(token, public_ip_id)['state']
    while(tries < max_tries and public_ip_state != "READY" and public_ip_state != "FAILED"):
        time.sleep(constants.INTERVAL_CHECK_PUBLIC_IP_STATE_SEC)
        public_ip_state = http_helper.get_public_ip(token, public_ip_id)['state']
        tries += 1
    if(public_ip_state == "READY"):
        return (True, constants.PUBLIC_IP_REQUEST_SUCCESSFUL_MESSAGE)
    elif(public_ip_state == "FAILED"):
        return (False, constants.PUBLIC_IP_REQUEST_FAILED_MESSAGE)
    elif(tries == max_tries):
        return (False, constants.PUBLIC_IP_REQUEST_MAX_TRIES_MESSAGE)

def create_resource(token, compute_spec):
    compute_id = http_helper.create_compute(token, compute_spec)
    result, message = sync_get_compute(token, compute_id, constants.INTERVAL_CHECK_COMPUTE_STATE_SEC, 20)
    
    if result:
        public_ip_id = http_helper.create_public_ip(token, compute_id)
        result, message = sync_get_public_ip(token, public_ip_id, constants.INTERVAL_CHECK_PUBLIC_IP_STATE_SEC, 20)
        if result:
            resource = {'compute_id':compute_id, 'public_ip_id':public_ip_id}
            return resource
        else:
            http_helper.delete_public_ip(token, public_ip_id)
            time.sleep(1)
            http_helper.delete_compute(token, compute_id)
            return message
    else:
        http_helper.delete_compute(token, compute_id)
        return message