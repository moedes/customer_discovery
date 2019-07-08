import requests
import json
import creds
import pandas as pd

session = requests.Session()
session.auth = (creds.login["username"], creds.login["password"])

portinfo = session.get('https://10.237.196.48/api/types/ipPort/instances?fields=name,macAddress,isLinkUp&compact=true', headers={"X-EMC-REST-CLIENT":"true"}, verify=False)
basicinfo = session.get('https://10.237.196.48/api/types/basicSystemInfo/instances?fields=name,model,softwareVersion&compact=true', headers={"X-EMC-REST-CLIENT":"true"}, verify=False)
poolinfo = session.get('https://10.237.196.48/api/types/pool/instances?compact=true', headers={"X-EMC-REST-CLIENT":"true"}, verify=False)

portinfo = portinfo.json()
basicinfo = basicinfo.json()

network = []
basic = []
sysinfo={}

for inter in portinfo['entries']:
    network.append(inter['content'])

for info in basicinfo['entries']:
    basic.append(info['content'])

sysinfo['Network'] = network

pretty_sysinfo = json.dumps(sysinfo, indent=2)

print(pretty_sysinfo)

df = pd.DataFrame(basic)

print(df)




# for unit in basicinfo['entries']:
#    swversion = unit['content']['softwareVersion']
#    name = unit['content']['name']
#    model = unit['content']['model']
#    print(name, model, swversion) 


# for interface in portinfo['entries']:
#     name = interface['content']['name']
#     mac = interface['content']['macAddress']
#     status = interface['content']['isLinkUp']
#     if status == True:
#         status = "Link is Up"
#     else:
#         status = "Link is Down"
#     print(name, mac, status)