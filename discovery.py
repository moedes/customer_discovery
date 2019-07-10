import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
import creds
import pandas as pd

session = requests.Session()
session.auth = (creds.login["username"], creds.login["password"])

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def UnityCon(UnityArr):

    sysinfo = {}    
    basicu = GetUnityBasic(UnityArr)
    portsu = GetUnityPorts(UnityArr)
    poolsu = GetUnityPools(UnityArr)
    swu = GetUnitySWInfo(UnityArr)
    snu = GetUnitySNInfo(UnityArr)
    syscapu = GetUnitySysCap(UnityArr)

    base_dict = {}

    #print(portsu)

    base_dict.update(portsu)
    base_dict.update(basicu)

    print(base_dict)

    # print(basicu)
    # print(poolsu)
    # print(portsu)

    sysinfo['Basic'] = basicu
    sysinfo['Network'] = portsu
    sysinfo['Pools'] = poolsu
    sysinfo['Software'] = swu
    sysinfo['SN'] = snu
    sysinfo['Capacity Info'] = syscapu
    # print(basicu)
    # labels = []
    # for base in basicu:
    #     for key in base.keys():
    #         labels.append(key)
        

    # print(labels)
    return


def GetUnityBasic(UnityArr):

    basicinfo = session.get('https://' + UnityArr + '/api/types/basicSystemInfo/instances?fields=name,model,softwareVersion&compact=true', headers={"X-EMC-REST-CLIENT":"true"}, verify=False)
    basicjson = basicinfo.json()
    basic_dict = {}
    basiclst = []
    for info in basicjson['entries']:
        basiclst.append(info['content'])

    for diction in basiclst:
        basic_dict.update(diction)

    basic_dict['sysname'] = basic_dict.pop('name')

    return basic_dict

def GetUnityPorts(UnityArr):

    portinfo = session.get('https://' + UnityArr + '/api/types/ipPort/instances?fields=name,macAddress,isLinkUp&compact=true', headers={"X-EMC-REST-CLIENT":"true"}, verify=False)
    portjson = portinfo.json()
    portjson.pop('id')
    port_dict = {}
    portlst = []
    for port in portjson['entries']:
        portlst.append(port['content'])
    
    for diction in portlst:
        print(diction)
        port_dict.update(diction)

    port_dict['portname'] = port_dict.pop('name')
    port_dict['System'] = UnityArr

    print(port_dict)

    return port_dict

    
def GetUnityPools(UnityArr):
    
    poolinfo = session.get('https://' + UnityArr + '/api/types/pool/instances?fields=name,type,isAllFlash,health,sizeTotal,sizeUsed,sizeFree,dataReductionRatio&compact=true', headers={"X-EMC-REST-CLIENT":"true"}, verify=False)
    pooljson = poolinfo.json()
    pool_dict = {}
    poollst = []
    for pool in pooljson['entries']:
        poollst.append(pool['content'])

    for diction in poollst:
        pool_dict.update(diction)

    pool_dict['poolname'] = pool_dict.pop('name')
    pool_dict['System'] = UnityArr

    print(pool_dict['System'])

    return pool_dict

def GetUnitySWInfo(UnityArr):
    
    swinfo = session.get('https://' + UnityArr + '/api/types/installedSoftwareVersion/instances?fields=version,revision&compact=true', headers={"X-EMC-REST-CLIENT":"true"}, verify=False)
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

unityip = ["10.237.196.48"]

for ip in unityip:
    
    UnityCon(ip)