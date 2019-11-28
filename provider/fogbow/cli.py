import argparse
import http_helper
import json
import fogbow
from config import *
import sys

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--imageId", default="",
                    help="Id of the compute image")
    ap.add_argument("-m", "--memory", default="",
                    help="Compute memory size")
    ap.add_argument("-c", "--vCPU", default="",
                    help="Amount of compute cpu")
    ap.add_argument("-d", "--disk", default="",
                    help="Compute disk size")
    args = vars(ap.parse_args())

    #TODO Add information about using args.
    args['publicKey'] = public_key
    args['name'] = default_compute_name
    my_token = http_helper.create_token()
    spec = http_helper.ComputeSpec.from_json(args)
    resource = fogbow.create_resource(my_token, spec)

    if(type(resource) is not dict):
        print(resource)
        sys.exit(1)
    else:
        print(resource)
        ip = http_helper.get_public_ip(my_token, resource['public_ip_id'])["ip"]
        print("ip ": ip)
        sys.exit(0)

if __name__== "__main__":
    main()