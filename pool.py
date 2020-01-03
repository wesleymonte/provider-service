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

default_public_key_path = os.path.realpath('./keys/pp.pub')

#TODO move to ansible template
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
    logging.info(messages.GETTING_POOLS)
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

def create_pool(pool_name):
    if pool_name == None or pool_name.strip() == "":
        logging.error("Error: " + messages.INVALID_POOL_NAME)
        raise Exception(messages.INVALID_POOL_NAME)
    pool_id = str(uuid.uuid4())
    storage.add_pool(pool_id, pool_name)
    logging.info(messages.CREATED_POOL.format(pool_name, pool_id))
    return pool_id

def get_node(pool_id, node_id):
    pool = get_pool(pool_id)
    if node_id not in pool.get("nodes"):
        logging.error(messages.NODE_NOT_FOUND.format(pool_id, node_id))
        raise Exception(messages.NODE_NOT_FOUND.format(pool_id, node_id))
    else:
        logging.info(messages.GOT_NODE.format(pool_id, node_id))
        return pool.get("nodes").get(node_id)

def validate_node_body(body):
    driver = body.get("driver")
    if driver not in ["fogbow", "dry"]:
        raise Exception(messages.INVALID_DRIVER)
    template = body.get("template")
    if template not in ["ansible-default"]:
        raise Exception(messages.INVALID_TEMPLATE)

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
        storage.save_node(pool_id, node_id, node)
        storage.set_node_state(pool_id, node_id, NodeState.PROVISIONED.value)
    except Exception as e:
        logging.error(messages.ERROR_RUNNING_DRIVER.format(driver, node_id, pool_id))
        storage.set_node_state(pool_id, node_id, NodeState.FAILED.value)
        raise e

def run_template(pool_id, node_id):
    template = storage.get_template(pool_id, node_id)
    try:
        storage.set_node_state(pool_id, node_id, NodeState.SETTING.value)
        if template == "ansible-default":
            node = storage.get_node(pool_id, node_id)
            ansible.run(node)
        storage.save_node(pool_id, node_id, node)
        storage.set_node_state(pool_id, node_id, NodeState.READY.value)
    except Exception as e:
        logging.error(messages.ERROR_RUNNING_TEMPLATE.format(driver, node_id, pool_id))
        storage.set_node_state(pool_id, node_id, NodeState.FAILED.value)
        raise e

def get_public_key():
    with open(default_public_key_path, 'r+') as file:
        return file.read()

#TODO move to ansible template
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