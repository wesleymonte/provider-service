import logging

def to_response(msg, result):
    return {"msg": msg, "result": result}

def validateRequestNodesBody(request):
    fields = ["provider", "amount", "spec"]
    for field in fields:
        if request.get(field) is None:
            logging.error("Not found field [{}] in request nodes".format(field))
            return False
    return validateNodeSpec(request.get("spec"))

def validateNodeSpec(spec):
    fields = ["name", "memory", "vCPU", "disk", "imageId"]
    for field in fields:
        if spec.get(field) is None:
            logging.error("Not found field [{}] in request nodes".format(field))
            return False
    return True
