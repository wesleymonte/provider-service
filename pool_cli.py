import click

default_storage_path = './storage/pools.json'
default_public_key_path = "./keys/pp.pub"

def load():
    # TODO Check if file exists
    with open(default_storage_path, 'r') as file:
        _pools = json.load(file)
    return _pools

def save(dict):
    with open(default_storage_path, 'w+') as file:
        json.dump(dict, file, sort_keys=True, indent=4)

@click.group()
def pool():
    """Pool CLI"""


@pool.command()
@pool.argument('name', nargs=1)
def create(name):
    pools = load()
    if name not in pools:
        pool = Pool(name, []).toDict()
        pools[name] = pool
        save(pools)
    else:
        print("Pool already exists")


@pool.command()
def status():
    print("Status")


@pool.command()
def add():
    print("Add")


if __name__ == '__main__':
    pool(prog_name='pool')
