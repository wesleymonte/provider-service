import requests
from config import *
import constants

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
    response = requests.get(ras_public_key_endpoint)
    publicKey = response.json()['publicKey']
    return publicKey

def create_token():
    ras_public_key = get_ras_public_key()
    response = requests.post(as_token_endpoint,
                headers={'Content-Type':'application/json'},
                json={'credentials':{'username':as_token_username, 'password':as_token_password},
                        'publicKey':ras_public_key})
    token = response.json()['token']
    return token

def create_compute(token, compute_spec):
    response = requests.post(ras_compute_endpoint,
                json=compute_spec.to_json(), 
                headers={'Fogbow-User-Token':token, 'Content-Type':'application/json'})
    compute_id = response.json()['id']
    return compute_id

def get_compute(token, compute_id):
    response = requests.get(ras_compute_endpoint + "/" + compute_id,
                headers={'Fogbow-User-Token':token})
    return response.json()

def delete_compute(token, compute_id):
    response = requests.delete(ras_compute_endpoint + "/" + compute_id,
                headers={'Fogbow-User-Token':token})

def create_public_ip(token, compute_id):
    response = requests.post(ras_public_ip_endpoint,
                headers={'Fogbow-User-Token':token, 'Content-Type':'application/json'},
                json={'computeId':compute_id})
    public_ip_id = response.json()['id']
    return public_ip_id

def get_public_ip(token, public_ip_id):
    response = requests.get(ras_public_ip_endpoint + "/" + public_ip_id, 
                headers={'Fogbow-User-Token':token})
    return response.json()

def delete_public_ip(token, public_ip_id):
    response = requests.delete(ras_public_ip_endpoint + "/" + public_ip_id,
                headers={'Fogbow-User-Token':token})
    return response.json()

def get_images(token):
    response = requests.get(ras_images,
                headers={'Fogbow-User-Token':token})
    return response.json()