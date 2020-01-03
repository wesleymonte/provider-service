import logging
import json
import os
from filelock import FileLock
import uuid

pools_storage=os.path.realpath('./storage/pools.json')
pools_lock = os.path.realpath('./storage/pools.json.lock')

orders_storage=os.path.realpath('./storage/orders.json')
orders_lock = os.path.realpath('./storage/orders.json.lock')

def load_pools():
    logging.debug("Loading storage file")
    # TODO Check if file exists
    with open(pools_storage, 'r') as file:
        _pools = json.load(file)
    return _pools

def save_pools(data):
    with open(pools_storage, 'w+') as file:
        json.dump(data, file, sort_keys=True, indent=4)

def add_pool(pool_id, pool_name):
    lock = FileLock(pools_lock)
    with lock:
        pools = load_pools()
        pools[pool_id] = {"id": pool_id, "name":pool_name, "nodes":[]}
        save_pools(pools) 

def add_node(pool_name, ip):
    lock = FileLock(pools_lock)
    with lock:
        pools = load_pools()
        pools[pool_name]["nodes"].append({"ip":ip, "state":"not_provisioned"})
        save_pools(pools)

def add_node(pool_id, node_id, driver, template, spec):
    lock = FileLock(pools_lock)
    with lock:
        pools = load_pools()
        pools[pool_id]["nodes"][node_id] = {"driver":driver, "spec":spec, "template": template, "state":"CREATE"}
        save_pools(pools)

def save_node(pool_id, node_id, node):
    lock = FileLock(pools_lock)
    with lock:
        pools = load_pools()
        pools[pool_id]["nodes"][node_id] = node
        save_pools(pools)

def set_node_state(pool_id, node_id, state):
    lock = FileLock(pools_lock)
    with lock:
        pools = load_pools()
        pools[pool_id]["nodes"][node_id]["state"] = state
        save_pools(pools)

def get_node(pool_id, node_id):
    lock = FileLock(pools_lock)
    with lock:
        pools = load_pools()
        return pools.get(pool_id).get("nodes").get(node_id)

def get_attribute_from_node(pool_id, node_id, attribute):
    lock = FileLock(pools_lock)
    with lock:
        pools = load_pools()
        return pools.get(pool_id).get("nodes").get(node_id).get(attribute)

def get_driver(pool_id, node_id):
    return get_attribute_from_node(pool_id, node_id, "driver")

def get_template(pool_id, node_id):
    return get_attribute_from_node(pool_id, node_id, "template")

def get_pool(pool_name):
    lock = FileLock(pools_lock)
    with lock:
        pools = load_pools()
        return pools.get(pool_name)