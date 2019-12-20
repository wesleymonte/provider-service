def check_spec(node):
    spec = node.get("spec")
    if spec == None or spec.get("ip") == None:
        raise Exception("Invalid node specification [{}]".format(node.get("id")))

def provider(node):
    #TODO ssh ping
    check_spec(node)
    ip = node.get("spec").get("ip")
    node["ip"] = ip
