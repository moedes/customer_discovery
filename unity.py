import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
import creds
# import pandas as pd

session = requests.Session()
session.auth = (creds.unitylogin["username"], creds.unitylogin["password"])

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class UnitySystem:

    def __init__(self, UnityArr):
        self.UnityArr = UnityArr

    def GetUnityBasic(self):
        
        mypath = 'https://' + self.UnityArr + '/api/types/basicSystemInfo/instances?fields=name,model,softwareVersion&compact=true'

        basicinfo = session.get(mypath, headers={"X-EMC-REST-CLIENT":"true"}, verify=False)
        
        if basicinfo.status_code == 200:
        
            basicjson = basicinfo.json()
            basiclst = []
            for info in basicjson['entries']:
                basiclst.append(info['content'])
        
        return basiclst

    def GetUnityPorts(self):

        portinfo = session.get('https://' + self.UnityArr + '/api/types/ipPort/instances?fields=name,macAddress,isLinkUp&compact=true', headers={"X-EMC-REST-CLIENT":"true"}, verify=False)
        
        if portinfo.status_code == 200:
        
            portjson = portinfo.json()
            portlst = []
            for port in portjson['entries']:
                portlst.append(port['content'])
        
        return portlst

        
    def GetUnityPools(self):
        
        poolinfo = session.get('https://' + self.UnityArr + '/api/types/pool/instances?fields=name,type,isAllFlash,health,sizeTotal,sizeUsed,sizeFree,dataReductionRatio&compact=true', headers={"X-EMC-REST-CLIENT":"true"}, verify=False)
        
        if poolinfo.status_code == 200:
                
            pooljson = poolinfo.json()
            poollst = []
            for pool in pooljson['entries']:
                poollst.append(pool['content'])

            for pooldic in poollst:
                for key, value in pooldic.items():
                    if key == "sizeTotal":
                        totalsizeTB = round(value/1099511627776, 2)
                        pooldic[key] = totalsizeTB
                    if key == "sizeUsed":
                        usedsizeTB = round(value/1099511627776, 2)
                        pooldic[key] = usedsizeTB
                    if key == "sizeFree":
                        freesizeTB = round(value/1099511627776, 2)
                        pooldic[key] = freesizeTB
                pooldic['Percent Free'] = round((freesizeTB/totalsizeTB) * 100, 2)

        return poollst

    def GetUnitySWInfo(self):
        
        swinfo = session.get('https://' + self.UnityArr + '/api/types/installedSoftwareVersion/instances?fields=version,revision&compact=true', headers={"X-EMC-REST-CLIENT":"true"}, verify=False)
        
        if swinfo.status_code == 200:

            swjson = swinfo.json()
            swinfolst =[]
            for sw in swjson['entries']:
                swinfolst.append(sw['content'])

        return swinfolst

    def GetUnitySNInfo(self):

        sninfo = session.get('https://' + self.UnityArr + '/api/types/system/instances?fields=serialNumber&compact=true', headers={"X-EMC-REST-CLIENT":"true"}, verify=False)
        
        if sninfo.status_code == 200:
                
            snjson = sninfo.json()
            sninfolst = []
            for sn in snjson['entries']:
                sninfolst.append(sn['content'])

        return sninfolst

    def GetUnitySysCap(self):

        syscapinfo = session.get('https://' + self.UnityArr + '/api/types/systemCapacity/instances?fields=sizeTotal,sizeUsed,sizeFree,dataReductionRatio,overallEfficiencyRatio&compact=true', headers={"X-EMC-REST-CLIENT":"true"}, verify=False)
        
        if syscapinfo.status_code == 200:
            
            syscapjson = syscapinfo.json()
            syscaplst = []
            for sys in syscapjson['entries']:
                syscaplst.append(sys['content'])

            for syscapdic in syscaplst:
                for key, value in syscapdic.items():
                    if key == "sizeTotal":
                        totalsizeTB = round(value/1099511627776, 2)
                        syscapdic[key] = totalsizeTB
                    if key == "sizeUsed":
                        usedsizeTB = round(value/1099511627776, 2)
                        syscapdic[key] = usedsizeTB
                    if key == "sizeFree":
                        freesizeTB = round(value/1099511627776, 2)
                        syscapdic[key] = freesizeTB
                
        return syscaplst

    def GetUnityFSInfo(self):
        
        fsinfo = session.get('https://' + self.UnityArr + '/api/types/filesystem/instances?fields=name,type,supportedProtocols,sizeAllocated,sizeAllocatedTotal,sizeTotal,sizeUsed,dataReductionRatio,storageResource.name,pool.name,nasServer.name,cifsShare.name,cifsShare.exportPaths,nfsShare.name,nfsShare.exportPaths', headers={"X-EMC-REST-CLIENT":"true"}, verify=False)
        
        if fsinfo.status_code == 200:
            
            fsinfojson = fsinfo.json()
            fsinfolst = []

            for fs in fsinfojson['entries']:
                fsinfolst.append(fs['content'])

            for fsinfodic in fsinfolst:
                for key, value in fsinfodic.items():
                    if key == "sizeTotal":
                        totalsizeTB = round(value/1099511627776, 2)
                        fsinfodic[key] = totalsizeTB
                    if key == "sizeUsed":
                        usedsizeTB = round(value/1099511627776, 2)
                        fsinfodic[key] = usedsizeTB
                    if key == "sizeAllocated":
                        sizeAllocatedTB = round(value/1099511627776, 2)
                        fsinfodic[key] = sizeAllocatedTB
                    if key == "sizeAllocatedTotal":
                        sizeAllocatedTotalTB = round(value/1099511627776, 2)
                        fsinfodic[key] = sizeAllocatedTotalTB
                    if key == "type":
                        if value == 1:
                            newvalue = "FileSystem"
                            fsinfodic[key] = newvalue
                        if value == 2:
                            newvalue = "VMWare NFS"
                            fsinfodic[key] = newvalue
        else:
            fsinfolst = []

        return fsinfolst