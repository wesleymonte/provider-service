import flask
from flask import request
from flask import jsonify
from flask import json
import os
import subprocess
import json as js
import provider.fogbow.fogbow
import pool

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/version', methods=['GET'])
def home():
    return {"version":"0.0.1"}

@app.route('/api/v1/pools', methods=['GET'])
def get_pools():
    response = pool.load()
    return response, 200

@app.route('/api/v1/pools/<poolname>', methods=['GET'])
def get_pool(poolname):
    args = ["status", poolname]
    response = pool.run_status(args)
    if not response.get("result"):
        return {"error": "Error while getting pool [" + poolname + "]: " + response.get("msg")}, 404
    return js.loads(response.get("msg")), 200

@app.route('/api/v1/pools', methods=['POST'])
def add_pool():
    if request.is_json:
        name = request.json.get("name")
        if name == None or name.strip() == "":
            return {"error":"invalid pool name"}, 400
        args=["create", name]
        response = pool.run_create(args)
        if not response.get("result"):
            return {"error": "Error while creating pool [" + name + "]: " + response.get("msg")}, 404
        return {"msg": response.get("msg")}, 200
    else:
        return {"error":"Invalid request"}, 400

@app.route('/api/v1/pools/<poolname>', methods=['POST'])
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

@app.route('/api/v1/provider/fogbow', methods=['POST'])
def request_to_fogbow_provider():
    if request.is_json:
        pool_id = request.json.get("pool_id")
        amount = request.json.get("amount")
        spec = request.json.get("spec")
        if spec != None:
            pool.async_provider_nodes(pool_id, spec, amount)
            return {"msg": "OK"}, 200
        else:
            return {"error": "Error while request fogbow resources [" + poolname + "]"}, 404
    else:
        return {"error":"Invalid request"}, 400


app.run()