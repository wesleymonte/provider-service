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

def add_pool(pool_name):
    lock = FileLock(pools_lock)
    with lock:
        pools = load_pools()
        pool = {"name":pool_name, "nodes":[], "orders":[]}
        pools[pool_name] = pool
        save_pools(pools)

def add_node(pool_name, ip):
    lock = FileLock(pools_lock)
    with lock:
        pools = load_pools()
        pools[pool_name]["nodes"].append({"ip":ip, "state":"not_provisioned"})
        save_pools(pools)

def add_node(pool_name, node_id, driver, spec):
    lock = FileLock(pools_lock)
    with lock:
        pools = load_pools()
        pools[pool_name]["nodes"][node_id] = {"driver":driver, "spec":spec, "state":"not_provisioned"})
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

def get_pool(pool_name):
    lock = FileLock(pools_lock)
    with lock:
        pools = load_pools()
        return pools.get(pool_name)

def load_orders():
    logging.debug("Loading storage file")
    # TODO Check if file exists
    with open(orders_storage, 'r') as file:
        _pools = json.load(file)
    return _pools

def save_orders(data):
    with open(orders_storage, 'w+') as file:
        json.dump(data, file, sort_keys=True, indent=4)

def create_order(pool_name, provider, amount, spec):
    lock_p = FileLock(pools_lock)
    lock_o = FileLock(orders_lock)

    order_id = str(uuid.uuid4())
    order = {"id":order_id, "pool":pool_name, "provider":provider, "amount": amount, "spec":spec, "state":"created", "provisioned":[]}

    with lock_p, lock_o:
        orders = load_orders()
        orders[order_id] = order
        save_orders(orders)
        pools = load_pools()
        pools[pool_name]["orders"].append(order_id)
        save_pools(pools)
    
    return order_id

def get_order(order_id):
    lock = FileLock(orders_lock)
    with lock:
        orders = load_orders()
        return orders[order_id]

def set_node_state(pool_name, ip, state):
    lock = FileLock(pools_lock)
    with lock:
        pools = load_pools()
        for node in pools[pool_name]["nodes"]:
            if node["ip"] == ip:
                node["state"] = state
                break
        save_pools(pools)

def set_order_state(order_id, state):
    lock = FileLock(orders_lock)
    with lock:
        orders = load_orders()
        orders[order_id]["state"]=state
        save_orders(orders)

def add_node_provisioned(order_id, ip):
    lock = FileLock(orders_lock)
    with lock:
        orders = load_orders()
        orders[order_id]["provisioned"].append(ip)
        save_orders(orders)

def check_finish_state(order_id):
    lock = FileLock(orders_lock)
    with lock:
        orders = load_orders()
        order = orders.get(order_id)
        if order.get("amount") == len((orders.get(order_id).get("provisioned"))):
            order["state"] = "finished"
            save_orders(orders)