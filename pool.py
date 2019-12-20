import json
import sys
import os
import subprocess
from util import to_response
from enum import Enum
import drivers.fogbow.fogbow as fogbow
import drivers.dry.dry as dry
import templates.ansible as ansible
import threading
import logging
import storage
from distutils.dir_util import copy_tree
import uuid
import shutil
import messages

class NodeState(Enum):
    CREATED = "CREATED"
    PROVISIONING = "PROVISIONING"
    PROVISIONED = "PROVISIONED"
    SETTING = "SETTING"
    READY = "READY"
    FAILED = "FAILED"

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

def validate_add_node_body(body):
    driver = body.get("driver")
    if driver not in ["fogbow", "dry"]:
        raise Exception(messages.INVALID_DRIVER)

def add_node(pool_id, driver, template, spec):
    node_id = str(uuid.uuid4())
    storage.add_node(pool_id, node_id, driver, template, spec)
    logging.info(messages.ADDED_NODE.format(node_id, pool_id))
    return node_id

def run_node(pool_id, node_id):
    try:
        run_driver(pool_id, node_id)
        run_template(pool_id, node_id)
    except Exception as e:
        logging.error(str(e))

def run_driver(pool_id, node_id):
    driver = storage.get_driver(pool_id, node_id)
    logging.info(messages.STARTING_DRIVER.format(driver, node_id, pool_id))
    try:
        storage.set_node_state(pool_id, node_id, NodeState.PROVISIONING.value)
        if driver == "fogbow":
            node = storage.get_node(pool_id, node_id)
            fogbow.provider(node)
        elif driver == "dry":
            dry.provider(node)
        storage.save_node(node)
        storage.set_node_state(pool_id, node_id, NodeState.PROVISIONED.value)
    except Exception as e:
        logging.error(messages.ERROR_RUNNING_DRIVER.format(driver, node_id, pool_id))
        storage.set_node_state(pool_id, node_id, NodeState.FAILED.value)
        raise e

def run_template(pool_id, node_id):
    template = storage.get_template()
    try:
        storage.set_node_state(pool_id, node_id, NodeState.SETTING.value)
        if template == "ansible-default":
            ansible.run(node)
        storage.set_node_state(pool_id, node_id, NodeState.READY.value)
    except Exception as e:
        logging.error(messages.ERROR_RUNNING_TEMPLATE.format(driver, node_id, pool_id))
        storage.set_node_state(pool_id, node_id, NodeState.FAILED.value)
        raise e


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