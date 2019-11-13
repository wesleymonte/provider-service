import json
import sys
import os
import subprocess
from util import to_response

default_storage_path = './storage/pools.json'
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

def write_ip(ip):
    config_file_path = "worker-deployment/hosts.conf"
    file = open(config_file_path, 'r')
    data = file.readlines()
    for i in range(len(data)):
        line = data[i]
        if line.find("deployed_worker_ip") == 0:
            data[i] = "deployed_worker_ip_1=" + ip + "\n"
            break
    file.close()
    file = open(config_file_path, 'w+')
    file.writelines(data)
    file.close()

# Run ansible given an ip and return an response
def provision(ip):
    write_ip(ip)
    _dir = "worker-deployment/"
    command = "bash install.sh"
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
    pools = load()
    _, pool_name = tokens
    if pool_name not in pools:
        pool = {"name":pool_name, "nodes":[]}
        pools[pool_name] = pool
        save(pools)
        return to_response("Create pool [" + pool_name + "]", True )
    else:
        return to_response("Pool already exists", False)

def run_provider(tokens):
    result = False
    msg = ""

    pools = load()
    _, pool_name, provider, ip = tokens
    if pool_name in pools:
        pool = pools[pool_name]
        for node in pool["nodes"]:
            if node["ip"] == ip:
                if provider == "ansible": 
                    node["state"] = "PROVISIONING"
                    result = provision(ip)
                    if result:
                        node["state"] = "PROVISIONED"
                        save(pools)
                        msg = "Node added successfully"
                        result = True
                    else:
                        node["state"] = "NOT_PROVISIONED"
                        msg = "An error occurred while running provider"
                else:
                    msg = "Provider not found!"
                break
        else:
            msg = "Ip not exists"
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
        if ip not in pool["nodes"]:
            if provider == "ansible":
                    pool["nodes"].append({"ip":ip, "state":"NOT_PROVISIONED"})
                    save(pools)
                    msg = "Node added successfully"
                    result = True
            else:
                msg = "Provider not found!"
        else:
            msg = "Pool already exists"
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