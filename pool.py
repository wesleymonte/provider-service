import json
import sys
import os
import subprocess
from util import to_response
from enum import Enum
import drivers.fogbow.fogbow as fogbow
import threading
import logging
import storage
from distutils.dir_util import copy_tree
import uuid
import shutil
import messages

class State(Enum):
    NOT_PROVISIONED = "not_provisioned"
    PROVISIONING = "provisioning"
    PROVISIONED = "provisioned"
    FAILED = "failed"

default_storage_path = os.path.realpath('./storage/pools.json')
default_lock_path = os.path.realpath('./storage/pools.json.lock')
default_public_key_path = os.path.realpath('./keys/pp.pub')

def cp_worker_deployment_folder(sufix):
    src="worker-deployment"
    dst="worker-deployment-" + sufix
    copy_tree(src, dst)
    return dst

def write_properties(config_file_path, ip, user):
    logging.debug("Config File Path: " + config_file_path)
    _file = open(config_file_path, 'r')
    data = _file.readlines()
    for i in range(len(data)):
        line = data[i]
        if line.find("deployed_worker_ip") == 0:
            data[i] = "deployed_worker_ip_1=" + ip + "\n"
        if line.find("remote_user") == 0:
            if user == None:
                data[i] = "remote_user=ubuntu\n"
            else:
                data[i] = "remote_user=" + user + "\n"
    _file.close()
    _file = open(config_file_path, 'w+')
    _file.writelines(data)
    _file.close()

# Run ansible given an ip and return an response
def provision(ip, user=None):
    folder = cp_worker_deployment_folder(str(uuid.uuid4())) + "/"
    config_file_path = folder + "hosts.conf"
    write_properties(config_file_path, ip, user)
    _dir = os.path.realpath(folder)
    command = "sudo bash install.sh"
    os.chdir(_dir)
    exit_value = os.system(command)
    exit_code = os.WEXITSTATUS(exit_value)
    os.chdir("..")
    shutil.rmtree(folder)
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

def get_pools():
    logging.info("Getting all pools")
    pools = storage.load_pools()
    return pools

def get_pool(pool_id):
    pools = storage.load_pools()
    if pool_id not in pools:
        logging.error(messages.POOL_NOT_FOUND.format(pool_id))
        raise Exception(messages.POOL_NOT_FOUND.format(pool_id))
    else:
        logging.info(messages.GOT_POOL.format(pool_id))
        pool = pools[pool_id]
        return pool

# TODO validate pool name
def create_pool(pool_name):
    if pool_name == None or pool_name.strip() == "":
        logging.error("Error: " + messages.INVALID_POOL_NAME)
        raise Exception(messages.INVALID_POOL_NAME)
    pool_id = str(uuid.uuid4())
    storage.add_pool(pool_id, pool_name)
    logging.info(messages.CREATED_POOL.format(pool_name, pool_id))
    return pool_id

def run_provider(tokens, user=None):
    logging.info("Running provider: " + str(tokens))
    result = False
    msg = ""

    pools = storage.load_pools()
    _, pool_name, provider, ip = tokens
    if pool_name in pools:
        pool = pools[pool_name]
        matching_ips = [node["ip"] for node in pool["nodes"] if node["ip"] == ip]
        if matching_ips:
            if provider == "ansible": 
                storage.set_node_state(pool_name, ip, State.PROVISIONING.value)
                result = provision(ip, user)
                if result:
                    logging.info("Node added successfully")
                    storage.set_node_state(pool_name, ip, State.PROVISIONED.value)
                    msg = "Node added successfully"
                    result = True
                else:
                    logging.info("An error occurred while running provider")
                    storage.set_node_state(pool_name, ip, State.FAILED.value)
                    msg = "An error occurred while running provider"
            else:
                msg = "Provider not found!"
        else:
            msg = "Ip not found"
    else:
        msg = "Pool not found!"
    return to_response(msg, result)

def add_node(pool_name, driver, spec):
    result = False
    msg = ""
    pools = storage.load_pools()
    if pool_name in pools:
        nodes = pools.get(pool_name).get("nodes")
        matching_ips = [ip for node_id in nodes if nodes.get(node_id).get("ip") == ip]
        if not matching_ips:
            node_id = str(uuid.uuid4())
            storage.add_node(pool_name, driver, spec)
            result = True
            msg = "Added node [{}] to pool [{}] wtih success".format(ip, pool_name)
            logging.info(msg)
        else:
            msg = "There is already a node with this ip [{}]".format(ip)
            logging.error(msg)
    else:
        msg = "No pool [{}] was found".format(pool_name)
    return to_response(msg, result)

def run_add(tokens):
    result = False
    msg = ""

    pools = storage.load_pools()
    _, pool_name, provider, ip = tokens
    if pool_name in pools:
        nodes = pools.get(pool_name).get("")
        matching_ips = [ip for node_id in pool.get("nodes") if pool.get("nodes").get(node_id).get("ip") == ip]
        if not matching_ips:
            if provider == "ansible":
                storage.add_node(pool_name, ip)
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
    pools = storage.load_pools()
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

def provider_node(order_id, pool_id, spec):
    spec["publicKey"] = get_public_key()
    ip = fogbow.request_node(spec)
    if ip != None:
        args=["", pool_id, "ansible", ip]
        run_add(args)
        run_provider(args, "fogbow")
        storage.add_node_provisioned(order_id, ip)
        storage.check_finish_state(order_id)

def async_run_order(order_id, pool_id, amount, spec):
    for _ in range(amount):
        threading.Thread(target=provider_node,args=(order_id, pool_id, spec,)).start()

def run_order(order_id):
    order = storage.get_order(order_id)
    storage.set_order_state(order_id, "running")
    async_run_order(order_id, order.get("pool"), order.get("amount"), order.get("spec"))

def create_order(pool_id, provider, amount, spec):
    order_id = storage.create_order(pool_id, provider, amount, spec)
    run_order(order_id)
    return order_id

def get_order(pool_id, order_id):
    pool = storage.get_pool(pool_id)
    order = None
    if order_id in pool.get("orders"):
        order = storage.get_order(order_id)
    return order