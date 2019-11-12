import pool
import sys

def print_response(response):
    print(response.get("msg"))

def main(args):
    cmd = args[0]
    # TODO validate number of tokens
    response = {"msg", "Not found command"}
    if cmd == "create":
        response = pool.run_create(args)
    elif cmd == "add":
        response = pool.run_add(args)
    elif cmd == "status":
        response = pool.run_status(args)
    elif cmd == "check":
        response = pool.run_check(args)
    elif cmd == "public-key":
        response = pool.get_public_key()
    print_response(response)

if __name__ == "__main__":
    args = sys.argv
    main(args[1:])