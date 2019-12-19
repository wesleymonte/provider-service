def cp_worker_deployment_folder(sufix):
    src="worker-deployment"
    dst="worker-deployment-" + sufix
    copy_tree(src, dst)
    return dst

def write_properties(config_file_path, ip, user):
    logging.debug("Config File Path: " + config_file_path)
    _file = open(config_file_path, 'r')
    data = _file.readlines()
    for i in range(len(data)):
        line = data[i]
        if line.find("deployed_worker_ip") == 0:
            data[i] = "deployed_worker_ip_1=" + ip + "\n"
        if line.find("remote_user") == 0:
            if user == None:
                data[i] = "remote_user=ubuntu\n"
            else:
                data[i] = "remote_user=" + user + "\n"
    _file.close()
    _file = open(config_file_path, 'w+')
    _file.writelines(data)
    _file.close()

def provision(ip, user=None):
    os.chdir("..")
    folder = cp_worker_deployment_folder(str(uuid.uuid4())) + "/"
    config_file_path = folder + "hosts.conf"
    write_properties(config_file_path, ip, user)
    _dir = os.path.realpath(folder)
    command = "sudo bash install.sh"
    os.chdir(_dir)
    exit_value = os.system(command)
    exit_code = os.WEXITSTATUS(exit_value)
    os.chdir("templates")
    shutil.rmtree(folder)
    if exit_code == 0:
        return True
    else:
        return False

def run(node):
