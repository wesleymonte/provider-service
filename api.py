import flask
from flask import request
from flask import jsonify
from flask import json
import os
import subprocess
import json as js
import pool
import logging
import util
import storage
import messages

app = flask.Flask(__name__)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

@app.route('/version', methods=['GET'])
def home():
    return {"version":"0.0.1"}

@app.route('/api/v1/pools', methods=['GET'])
def get_pools():
    pools = pool.get_pools()
    return pools, 200

@app.route('/api/v1/pools/<pool_id>', methods=['GET'])
def get_pool(pool_id):
    try:
        _pool = pool.get_pool(pool_id)
        return _pool, 200
    except Exception as e:
        return {"msg": messages.ERROR_MESSAGE.format(str(e))}, 400

@app.route('/api/v1/pools', methods=['POST'])
def add_pool():
    if request.is_json:
        try:
            name = request.json.get("name")
            pool_id = pool.create_pool(name)
            return {"id": pool_id}, 201
        except Exception as e:
            return {"msg": messages.ERROR_MESSAGE.format(str(e))}, 400
    else:
        return {"msg": messages.ERROR_MESSAGE.format(messages.INVALID_REQUEST)}, 400    

@app.route('/api/v1/pools/<poolname>/nodes', methods=['POST'])
def add_node(poolname):
    if request.is_json:
        provider = request.json.get("provider")
        ip = request.json.get("ip")
        if ip == None or ip.strip() == "":
            return {"error":"invalid ip"}, 400
        args=["add", poolname, provider, ip]
        response = pool.run_add(args)
        if not response.get("result"):
            return {"error": "Error while adding node [" + poolname + "]: " + response.get("msg")}, 404
        response = pool.run_provider(args)
        if not response.get("result"):
            return {"error": "Error while providering node [" + poolname + "]: " + response.get("msg")}, 404
        return {"msg": response.get("msg")}, 200
    else:
        return {"error":"Invalid request"}, 400

@app.route('/api/v1/pools/<poolname>/status', methods=['GET'])
def get_pool_status(poolname):
    args=["check", poolname, "ansible"]
    response = pool.run_check(args)
    if not response.get("result"):
        return {"error": "Error while checking node [" + poolname + "]"}, 404
    return response.get("msg"), 200

@app.route('/api/v1/publickey', methods=['GET'])
def get_public_key():
    response = pool.get_public_key()
    return {"public_key": response}

@app.route('/api/v1/orders', methods=['POST'])
def create_order():
    if request.is_json:
        if util.validateRequestNodesBody(request.json):
            amount = request.json.get("amount")
            spec = request.json.get("spec")
            logging.info("Requesting [{}] nodes from fogbow to [{}]".format(amount, poolname))
            order_id = pool.create_order(poolname, "fogbow", amount, spec)
            return {"id": order_id}, 201
        else:
            return {"error": "Malformed request body"}, 404
    else:
        return {"error":"Request body is not an json"}, 400

@app.route('/api/v1/orders/<order_id>', methods=['GET'])
def get_order(poolname, order_id):
    if request.is_json:
        order = pool.get_order(poolname, order_id)
        return order, 200
    else:
        return {"error":"Request body is not an json"}, 400

if __name__ == "__main__":
    app.run(debug=True)