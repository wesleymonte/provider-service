import requests
from config import *
from constants import *
import json
import os

config_holder = ConfigHolder(os.path.realpath(DEFAULT_CONFIG_FILE_NAME))

class ComputeSpec:
    def __init__(self, name=None, image_id=None, memory=None, vcpu=None, disk=None, public_key=None):
        self.name = name
        self.image_id = image_id
        self.memory = memory
        self.vcpu = vcpu
        self.disk = disk
        self.public_key = public_key
    
    def to_json(self):
        json = {}
        json['name'] = self.name
        json['imageId'] = self.image_id
        json['memory'] = self.memory
        json['vCPU'] = self.vcpu
        json['disk'] = self.disk
        json['publicKey'] = self.public_key
        return json
    
    @staticmethod
    def from_json(json):
        spec = ComputeSpec()
        spec.name = json.get('name')
        spec.image_id = json.get('imageId')
        spec.memory = json.get('memory')
        spec.vcpu = json.get('vCPU')
        spec.disk = json.get('disk')
        spec.public_key = json.get('publicKey')
        return spec


def get_ras_public_key():
    endpoint = config_holder.get_endpoint_from_ras(PUBLIC_KEY_EP_KEY)
    response = requests.get(endpoint)
    publicKey = response.json()['publicKey']
    return publicKey

def create_token():
    as_token_username=config_holder.get_as_property(TOKEN_USERNAME_KEY)
    as_token_password=config_holder.get_as_property(TOKEN_PASSWORD_KEY)
    endpoint = config_holder.get_endpoint_from_as(TOKEN_ENDPOINT_KEY)
    ras_public_key = get_ras_public_key()

    response = requests.post(endpoint,
                headers={'Content-Type':'application/json'},
                json={'credentials':{'username':as_token_username, 'password':as_token_password},
                        'publicKey':ras_public_key})
    token = response.json()['token']
    return token

def create_compute(token, compute_spec):
    endpoint = config_holder.get_endpoint_from_ras(COMPUTES_EP_KEY)
    body = compute_spec.to_json()
    response = requests.post(endpoint,
                json=body, 
                headers={'Fogbow-User-Token':token, 'Content-Type':'application/json'})
    compute_id = response.json()['id']
    return compute_id

def get_compute(token, compute_id):
    endpoint = config_holder.get_endpoint_from_ras(COMPUTES_EP_KEY)
    response = requests.get(endpoint + "/" + compute_id,
                headers={'Fogbow-User-Token':token})
    return response.json()

def delete_compute(token, compute_id):
    endpoint = config_holder.get_endpoint_from_ras(COMPUTES_EP_KEY)
    response = requests.delete(endpoint + "/" + compute_id,
                headers={'Fogbow-User-Token':token})

def create_public_ip(token, compute_id):
    endpoint = config_holder.get_endpoint_from_ras(PUBLIC_IP_EP_KEY)
    response = requests.post(endpoint,
                headers={'Fogbow-User-Token':token, 'Content-Type':'application/json'},
                json={'computeId':compute_id})
    public_ip_id = response.json()['id']
    return public_ip_id

def get_public_ip(token, public_ip_id):
    ras_public_ip_endpoint = config_holder.get_endpoint_from_ras(PUBLIC_IP_EP_KEY)
    response = requests.get(ras_public_ip_endpoint + "/" + public_ip_id, 
                headers={'Fogbow-User-Token':token})
    return response.json()

def delete_public_ip(token, public_ip_id):
    ras_public_ip_endpoint = config_holder.get_endpoint_from_ras(PUBLIC_IP_EP_KEY)
    response = requests.delete(ras_public_ip_endpoint + "/" + public_ip_id,
                headers={'Fogbow-User-Token':token})
    return response.json()

def get_images(token):
    response = requests.get(ras_images,
                headers={'Fogbow-User-Token':token})
    return response.json()