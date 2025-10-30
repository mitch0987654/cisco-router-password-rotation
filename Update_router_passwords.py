from netmiko import ConnectHandler
import random
import string
from keepercommander.__main__ import get_params_from_config
from keepercommander.commands.record_edit import RecordUpdateCommand
from keepercommander import api

keeperParams = get_params_from_config("config.json")
api.login(keeperParams)
api.sync_down(keeperParams)

def generateRandomPassword(length):
    LOWERCASE = string.ascii_lowercase
    UPPERCASE = string.ascii_uppercase
    DIGITS = string.digits
    SPECIAL_CHARS = "!@#$%^&*()-_+="
    all_chars = LOWERCASE + UPPERCASE + DIGITS + SPECIAL_CHARS
    secure_string = [
        random.choice(LOWERCASE),
        random.choice(UPPERCASE),
        random.choice(DIGITS),
        random.choice(SPECIAL_CHARS)
    ]
    remaining_length = length - len(secure_string) 
    for _ in range(remaining_length):
        secure_string.append(random.choice(all_chars))
    random.shuffle(secure_string)
    return "".join(secure_string)

def updateKeeperRecord(routerIP, passwordstr):
    record_search = api.search_records(keeperParams, routerIP)
    for record in record_search:
        if (routerIP == record.notes):
            print("found 1 keeper record matching search parameters: " + routerIP)
            print("Updating keeper record password to: " + passwordstr)
            RecordUpdateCommand().execute(keeperParams, record=record.record_uid, fields=['password=' + passwordstr])   

routers = [
    {"host":"192.168.1.1"},
    {"host":"192.168.1.2"},
    {"host":"192.168.1.3"},
]

for router in routers:
    try:
        print(f"\n Connecting to {router['host']} ...")
        conn = ConnectHandler(device_type="cisco_ios", username="my_radius_username", password="my_radius_password", **router)
        hostname = conn.find_prompt().strip("#>")

        # Push config
        print(f"Applying config to {hostname} ...")
        newsecret = generateRandomPassword(45) # generate the required length password
        
        config_commands = [
            f"username my_local_username secret {newsecret}"
        ]
        print(f"username my_local_username secret {newsecret}")
        output = conn.send_config_set(config_commands)
        print(output)

        # Save config
        conn.save_config()
        print(f"Changes saved on {hostname}")

        conn.disconnect()

        updateKeeperRecord(router['host'],newsecret)

    except Exception as e:
        print(f"Failed on {router['host']}: {e}")
    
