import json
import sys
import os
import subprocess
from util import to_response
from enum import Enum
from filelock import FileLock
import provider.fogbow.fogbow as fogbow
import threading

class State(Enum):
    NOT_PROVISIONED = "not_provisioned"
    PROVISIONING = "provisioning"
    PROVISIONED = "provisioned"
    FAILED = "failed"

default_storage_path = './storage/pools.json'
default_lock_path = './storage/pools.json.lock'
default_public_key_path = "./keys/pp.pub"

# Read from default path and return a dict
def load():
    # TODO Check if file exists
    with open(default_storage_path, 'r') as file:
        _pools = json.load(file)
    return _pools

# Saves a dict into a default path
def save(dict):
    with open(default_storage_path, 'w+') as file:
        json.dump(dict, file, sort_keys=True, indent=4)

def add_node(pool_name, ip):
    lock = FileLock(default_lock_path)
    with lock:
        pools = load()
        pools[pool_name]["nodes"].append({"ip":ip, "state":State.NOT_PROVISIONED.value})
        save(pools)

def update_node_state(pool_name, ip, state):
    lock = FileLock(default_lock_path)
    with lock:
        pools = load()
        for node in pools[pool_name]["nodes"]:
            if node["ip"] == ip:
                node["state"] = state
                break
        save(pools)

def write_properties(ip, user):
    config_file_path = "worker-deployment/hosts.conf"
    file = open(config_file_path, 'r')
    data = file.readlines()
    for i in range(len(data)):
        line = data[i]
        if line.find("deployed_worker_ip") == 0:
            data[i] = "deployed_worker_ip_1=" + ip + "\n"
        if line.find("remote_user") == 0:
            if user == None:
                data[i] = "rmeote_user=ubuntu\n"
            else:
                data[i] = "remote_user=" + user + "\n"
    file.close()
    file = open(config_file_path, 'w+')
    file.writelines(data)
    file.close()

# Run ansible given an ip and return an response
def provision(ip, user=None):
    write_properties(ip, user)
    _dir = "worker-deployment/"
    command = "sudo bash install.sh"
    os.chdir(_dir)
    exit_value = os.system(command)
    exit_code = os.WEXITSTATUS(exit_value)
    os.chdir("..")
    if exit_code == 0:
        return True
    else:
        return False

def check(ip):
    write_ip(ip)
    _dir = "worker-deployment/"
    command = "bash check.sh"
    os.chdir(_dir)
    exit_value = os.system(command)
    exit_code = os.WEXITSTATUS(exit_value)
    os.chdir("..")
    if exit_code == 0:
        return True
    else:
        return False

def run_status(tokens):
    pools = load()
    _, pool_name = tokens
    if pool_name in pools:
        pool = pools[pool_name]
        return to_response(json.dumps(pool, indent=4, sort_keys=True), True)
    else:
        return to_response("Pool not found!", False)

# TODO validate pool name
def run_create(tokens):
    lock = FileLock(default_lock_path)
    with lock:
        pools = load()
        _, pool_name = tokens
        if pool_name not in pools:
            pool = {"name":pool_name, "nodes":[]}
            pools[pool_name] = pool
            save(pools)
            return to_response("Create pool [" + pool_name + "]", True )
        else:
            return to_response("Pool already exists", False)

def run_provider(tokens, user=None):
    result = False
    msg = ""

    pools = load()
    _, pool_name, provider, ip = tokens
    if pool_name in pools:
        pool = pools[pool_name]
        matching_ips = [node["ip"] for node in pool["nodes"] if node["ip"] == ip]
        if matching_ips:
            if provider == "ansible": 
                update_node_state(pool_name, ip, State.PROVISIONING.value)
                result = provision(ip, user)
                if result:
                    update_node_state(pool_name, ip, State.PROVISIONED.value)
                    msg = "Node added successfully"
                    result = True
                else:
                    update_node_state(pool_name, ip, State.FAILED.value)
                    msg = "An error occurred while running provider"
            else:
                msg = "Provider not found!"
        else:
            msg = "Ip not found"
    else:
        msg = "Pool not found!"
    return to_response(msg, result)

def run_add(tokens):
    result = False
    msg = ""

    pools = load()
    _, pool_name, provider, ip = tokens
    if pool_name in pools:
        pool = pools[pool_name]
        matching_ips = [node["ip"] for node in pool["nodes"] if node["ip"] == ip]
        if not matching_ips:
            if provider == "ansible":
                add_node(pool_name, ip)
                msg = "Node added successfully"
                result = True
            else:
                msg = "Provider not found!"
        else:
            result = True
            msg = "Node already exists"
    else:
        msg = "Pool not found!"
    return to_response(msg, result)

def get_public_key():
    with open(default_public_key_path, 'r+') as file:
        return file.read()

def run_check(tokens):
    result = False
    msg = ""
    pools = load()
    _, pool_name, provider = tokens
    if pool_name in pools:
        pool = pools[pool_name]
        if provider == "ansible":
            result = True
            nodes = {}
            for ip in pool["nodes"]:
                status = check(ip)
                if status:
                    nodes[ip] = "OK"
                else:
                    nodes[ip] = "FAILED"
            return to_response(nodes, result)
        else:
            msg = "Provider not found!"
    else:
        msg = "Pool not found!"
    return to_response(msg, result)

def provider_node(pool_id, spec):
    spec["publicKey"] = get_public_key()
    ip = fogbow.request_node(spec)
    args=["", pool_id, "ansible", ip]
    run_add(args)
    run_provider(args, "fogbow")

def async_provider_nodes(pool_id, spec, amount):
    for _ in range(amount):
        threading.Thread(target=provider_node,args=(pool_id, spec,)).start()

    

