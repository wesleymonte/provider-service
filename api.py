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
import threading

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

@app.route('/api/v1/pools/<pool_id>/nodes', methods=['POST'])
def add_node(pool_id):
    if request.is_json:
        try:
            pool.validate_add_node_body(request.json)

            driver = request.json.get("driver")
            template = request.json.get("template")
            spec = request.json.get("spec")

            node_id = pool.add_node(pool_id, driver, template, spec)
            threading.Thread(target=pool.run_node,args=(pool_id, node_id,)).start()
            return {"id": node_id}, 201
        except Exception as e:
            return {"msg": messages.ERROR_MESSAGE.format(str(e))}, 400
    else:
        return {"msg": messages.ERROR_MESSAGE.format(messages.INVALID_REQUEST)}, 400  

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

if __name__ == "__main__":
    app.run(debug=True)