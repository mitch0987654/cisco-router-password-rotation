from netmiko import ConnectHandler
from keepercommander.__main__ import get_params_from_config
from keepercommander.commands.record_edit import RecordUpdateCommand
from keepercommander import api

keeperParams = get_params_from_config("config.json")
api.login(keeperParams)
api.sync_down(keeperParams)

def getKeeperPasswordForRouter(routerIP):
    record_search = api.search_records(keeperParams, routerIP)
    for record in record_search:
        if (routerIP == record.notes):
            return ("" + record.password)
            #print("title:" + record.title, ", password:" + record.password, ", notes:" + record.notes)

routers = [
    {"host":"192.168.1.1"},
    {"host":"192.168.1.2"},
    {"host":"192.168.1.3"},
]

for dev in routers:
    try:
        print(f"--------Test block for {dev['host']}--------")
        print(f"  Connecting to {dev['host']} with radius creds...")
        conn = ConnectHandler(device_type="cisco_ios", username="my_radius_username", password="my_radius_password", **dev)
        hostname = conn.find_prompt().strip("#>")
        print(f"  Applying config to {hostname} to undo radius login preference...")
        config_commands = [
            "aaa authentication login default local",
            "aaa authorization exec default local if-authenticated"
        ]
        output = conn.send_config_set(config_commands)
        print(f"  Applied config to {hostname} successfully...")
        #print(output)
        conn.disconnect()

        print(f"  Test connecting to {dev['host']} with local creds...")
        newsecret = getKeeperPasswordForRouter(dev['host'])
        conn = ConnectHandler(device_type="cisco_ios", username="my_local_username", password=newsecret, secret="my_enable_password", **dev)
        conn.enable()
        #print("executing -----show running-config | inc aaa-----")
        output = conn.send_command("show running-config | inc aaa")
        print(f"  Successful connecting to {dev['host']} with local creds and running test command..")
        #print(output)
        print(f"  Applying config to {hostname} to redo radius login preference...")
        config_commands = [
            "aaa authentication login default group RAD_SVR local",
            "aaa authorization exec default group RAD_SVR local if-authenticated"
        ]
        output = conn.send_config_set(config_commands)
        print(f"  Applied config to {hostname} successfully...")
        #print(output)
        conn.disconnect()

        print(f"  Testing connecting to {dev['host']} with radius creds again...")
        conn = ConnectHandler(device_type="cisco_ios", username="my_radius_username", password="my_radius_password", **dev)
        #print("executing -----show running-config | inc aaa-----")
        output = conn.send_command("show running-config | inc aaa")
        #print(output)
        print(f"  Successful connecting to {dev['host']} with local creds and running test command..")
        conn.disconnect()        

    except Exception as e:
        print(f"  Failed on {dev['host']}: {e}")
    
