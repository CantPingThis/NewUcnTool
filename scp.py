#--// FAIRE UN YUM INSTALL SSHPASS SUR LE DOCKER GROOT


import os
from netmiko import ConnectHandler





#------------------------
#--// METHODE A RAJOUTER DANS LA CLASS PRECHECKS
#------------------------

def scp_process_management(hostname, username, password, enabled=None):
    
    try:
        with ConnectHandler(device_type='cisco_ios', ip=hostname, username=username, password=password) as net_connect:
            if enabled is True:
                net_connect.send_config_set(f'ip scp server enable')
            elif enabled is False:
                net_connect.send_config_set(f'no ip scp server enable')
            else:
                print('incorrect input user. arguement enabled must be "True or False"')

            output = net_connect.send_command('show running-config | include ip scp server enable')
            if 'ip scp server enable' in output:
                return True
            else:
                return False

    except Exception as e:
        print(e)


def push_file_to_remote_server(local_path, remote_path, hostname, username, password):
    command = f"scp -O {local_path} {username}@{hostname}:{remote_path}"
    os.system(f"echo {password} | sshpass -p {password} {command} < /dev/tty")








#------------------------
#--// A RAJOUTER DANS LE MAIN
#------------------------


#--// activation du serveur SCP sur le switch
scp_enable = scp_process_management('10.0.200.1', 'cotorep', 'StrongPassoword', enabled=True)

#--// si tout s'est bien passe, on pousse via SCP
if scp_enable is True:
    push_file_to_remote_server('/home/godzilarge/file.txt', 'flash:/file.txt', 'x.x.x.x', 'cotorep', 'StrongPassoword')


#--// enfin on desactive la partie scp server sur le switch
scp_disable = scp_process_management('10.0.200.1', 'cotorep', 'StrongPassoword', enabled=False)
