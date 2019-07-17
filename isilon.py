import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
import creds
from capconverter import convert

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

isisession = requests.Session()
isisession.auth = ('root', 'MRD3nver!')

isinodeinfo = isisession.get('https://10.237.194.43:8080/platform/7/cluster/nodes', verify=False).json()
isinameinfo = isisession.get('https://10.237.194.43:8080/platform/5/cluster/identity', verify=False).json()
isismbshareinfo = isisession.get('https://10.237.194.43:8080/platform/7/protocols/smb/shares?limit=5', verify=False).json()
isipoolsinfo = isiinfo = isisession.get('https://10.237.194.43:8080/platform/3/storagepool/storagepools', verify=False).json()

#print(json.dumps(isinodeinfo, indent=4))
ssdtotal = 0
hddtotal = 0

for node in isinodeinfo['nodes']:
    #print(json.dumps(node['status'], indent=2))
    model = node['hardware']['model']
    sn = node['hardware']['serial_number']
    version = node['status']['release']
    capacity = node['status']['capacity']
    nodeinfo = node['hardware']['product']
    for cap in capacity:
        if cap['type'] == 'SSD':
            ssdtotal = ssdtotal + cap['bytes']
        elif cap['type'] == 'HDD':
            hddtotal = hddtotal + cap['bytes']
        else:
            print('Error getting drive type or drive type not found')
    
if ssdtotal == 0 or hddtotal == 0:
    if ssdtotal == 0:
        print('No SSDs Found')
    else:
        print('No HDDs Found')
else:
    print('Drives Found')
        
    
hddcaptoTB = convert.bytestoTB(hddtotal)
ssdcaptoTB = convert.bytestoTB(ssdtotal)
print("SSD Total: " + str(ssdcaptoTB))
print("HDD Total: " + str(hddcaptoTB))

    
    
    #print(model + " " + sn + " " + version)

#for pool in isipoolsinfo['storagepools']:


    #print("pool name = " + pool['name'] + " pool type = " + pool['type'])

print(isinameinfo['name'])
#print(json.dumps(isismbshareinfo, indent=4))