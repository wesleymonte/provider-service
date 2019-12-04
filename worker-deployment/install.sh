#!/bin/bash

MY_PATH="`dirname \"$0\"`"              
MY_PATH="`( cd \"$MY_PATH\" && pwd )`" 

if [ -z "$MY_PATH" ] ; then
  # For some reason, the path is not accessible
  # to the script (e.g. permissions re-evaled after suid)
  exit 1
fi

HOSTS_CONF_FILE=$MY_PATH"/hosts.conf"

# Remote user of the host
readonly REMOTE_USER_PATTERN="remote_user"
readonly ANSIBLE_FILES_PATH_PATTERN="ansible_files_path"
readonly PRIVATE_KEY_FILE_PATH_PATTERN="ansible_ssh_private_key_file"
readonly DEPLOYED_WORKER_IP_PATTERN="deployed_worker_ip"
readonly DESTINATION_PATH_PATTERN="destination_path"
readonly DEPLOY_WORKER_YML_FILE="deploy-worker.yml"

readonly ANSIBLE_FILES_PATH=$(grep $ANSIBLE_FILES_PATH_PATTERN $HOSTS_CONF_FILE | awk -F "=" '{print $2}')
readonly REMOTE_USER=$(grep ${REMOTE_USER_PATTERN} ${HOSTS_CONF_FILE} | awk -F "=" '{print $2}')
readonly PRIVATE_KEY_FILE_PATH=$(grep $PRIVATE_KEY_FILE_PATH_PATTERN $HOSTS_CONF_FILE | awk -F "=" '{print $2}')
readonly DESTINATION_PATH="/home/${REMOTE_USER}"

readonly ANSIBLE_HOSTS_FILE=${ANSIBLE_FILES_PATH}/"hosts"
readonly ANSIBLE_CFG_FILE=${ANSIBLE_FILES_PATH}/"ansible.cfg"

# Writes the path of the private key file in Ansible hosts file
sed -i "s#.*$PRIVATE_KEY_FILE_PATH_PATTERN=.*#$PRIVATE_KEY_FILE_PATH_PATTERN=$PRIVATE_KEY_FILE_PATH#" $ANSIBLE_HOSTS_FILE
sed -i "s#.*$DESTINATION_PATH_PATTERN=.*#$DESTINATION_PATH_PATTERN=$DESTINATION_PATH#" $ANSIBLE_HOSTS_FILE
sed -i "s/.*$REMOTE_USER_PATTERN = .*/$REMOTE_USER_PATTERN = $REMOTE_USER/" $ANSIBLE_CFG_FILE

sed -i '/\[worker-machine\]/,/\[worker-machine:vars\]/{//!d}' $ANSIBLE_HOSTS_FILE

grep $DEPLOYED_WORKER_IP_PATTERN $HOSTS_CONF_FILE| while read -r line ; do
    DEPLOYED_WORKER_IP=$(echo $line | awk -F "=" '{print $2}')
    sed -i "/\[worker-machine:vars\]/i ${DEPLOYED_WORKER_IP}" $ANSIBLE_HOSTS_FILE
done

(cd $ANSIBLE_FILES_PATH && ansible-playbook -vvv $DEPLOY_WORKER_YML_FILE)
exit $?