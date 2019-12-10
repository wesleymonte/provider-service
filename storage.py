import logging
import json
import os
from filelock import FileLock

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

def add_pool(pool_name):
    lock = FileLock(pools_lock)
    with lock:
        pools = load_pools()
        pool = {"name":pool_name, "nodes":[]}
        pools[pool_name] = pool
        save_pools(pools)

def add_node(pool_name, ip):
    lock = FileLock(pools_lock)
    with lock:
        pools = load_pools()
        pools[pool_name]["nodes"].append({"ip":ip, "state":"not_provisioned"})
        save_pools(pools)

def set_node_state(pool_name, ip, state):
    lock = FileLock(pools_lock)
    with lock:
        pools = load_pools()
        for node in pools[pool_name]["nodes"]:
            if node["ip"] == ip:
                node["state"] = state
                break
        save_pools(pools)