import flask
from flask import request
from flask import jsonify
from flask import json
import os
import subprocess
import pool
import json as js

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

app.run(host='0.0.0.0')