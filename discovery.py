import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
import creds
import pandas as pd

session = requests.Session()
session.auth = (creds.login["username"], creds.login["password"])

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def GetUnityBasic(UnityArr):

    basicinfo = session.get('https://' + UnityArr + '/api/types/basicSystemInfo/instances?fields=name,model,softwareVersion&compact=true', headers={"X-EMC-REST-CLIENT":"true"}, verify=False)
    basicjson = basicinfo.json()
    basiclst = []
    for info in basicjson['entries']:
        basiclst.append(info['content'])

    return basiclst

def GetUnityPorts(UnityArr):

    portinfo = session.get('https://' + UnityArr + '/api/types/ipPort/instances?fields=name,macAddress,isLinkUp&compact=true', headers={"X-EMC-REST-CLIENT":"true"}, verify=False)
    portjson = portinfo.json()
    portlst = []
    for port in portjson['entries']:
        portlst.append(port['content'])

    return portlst


def GetUnityPools(UnityArr):
    
    poolinfo = session.get('https://' + UnityArr + '/api/types/pool/instances?fields=id,name,type,isAllFlash,health,sizeTotal,sizeUsed,sizeFree,dataReductionRatio&compact=true', headers={"X-EMC-REST-CLIENT":"true"}, verify=False)
    pooljson = poolinfo.json()
    poollst = []
    for pool in pooljson['entries']:
        poollst.append(pool['content'])

    return poollst

def GetUnitySWInfo(UnityArr):
    
    swinfo = session.get('https://' + UnityArr + '/api/types/installedSoftwareVersion/instances?fields=id,version,revision&compact=true', headers={"X-EMC-REST-CLIENT":"true"}, verify=False)
    swjson = swinfo.json()
    swinfolst =[]
    for sw in swjson['entries']:
        swinfolst.append(sw['content'])

    return swinfolst

def GetUnitySNInfo(UnityArr):

    sninfo = session.get('https://' + UnityArr + '/api/types/system/instances?fields=serialNumber&compact=true', headers={"X-EMC-REST-CLIENT":"true"}, verify=False)
    snjson = sninfo.json()
    sninfolst = []
    for sn in snjson['entries']:
        sninfolst.append(sn['content'])

    return sninfolst

def GetUnitySysCap(UnityArr):

    syscapinfo = session.get('https://' + UnityArr + '/api/types/systemCapacity/instances?fields=sizeTotal,sizeUsed,sizeFree,dataReductionRatio,overallEfficiencyRatio&compact=true', headers={"X-EMC-REST-CLIENT":"true"}, verify=False)
    syscapjson = syscapinfo.json()
    syscaplst = []
    for sys in syscapjson['entries']:
        syscaplst.append(sys['content'])

    return syscaplst

network = []

sysinfo={}

#pretty_sysinfo = json.dumps(sysinfo, indent=2)

#print(pretty_sysinfo)

unityip = ["10.237.196.48", "10.237.196.198"]

for ip in unityip:
    
    print(GetUnityBasic(ip))
    print(GetUnityPorts(ip))
    print(GetUnityPools(ip))
    print(GetUnitySWInfo(ip))
    print(GetUnitySNInfo(ip))
    print(GetUnitySysCap(ip))