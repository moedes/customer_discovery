import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
import creds
import pandas as pd
import xlsxwriter

session = requests.Session()
session.auth = (creds.login["username"], creds.login["password"])

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def UnityCon(UnityArr, workbook):

    sysinfo = {}    
    #basicu = GetUnityBasic(UnityArr)
    portsu = GetUnityPorts(UnityArr)
    poolsu = GetUnityPools(UnityArr)
    swu = GetUnitySWInfo(UnityArr)
    snu = GetUnitySNInfo(UnityArr)
    syscapu = GetUnitySysCap(UnityArr)

    print(poolsu)
       
    sysinfo['Basic'] = GetUnityBasic(UnityArr)
    sysinfo['Network'] = portsu
    sysinfo['Pools'] = poolsu
    sysinfo['Software'] = swu
    sysinfo['SN'] = snu
    sysinfo['Capacity Info'] = syscapu

    print(sysinfo['Pools'])

    #sysinfo_json = json.dumps(sysinfo, indent=4)

    basiclen = len(sysinfo['Basic'])
    snlen = len(sysinfo['SN'])
    caplen = len(sysinfo['Capacity Info'])
    poollen = len(sysinfo['Pools'])

    #for pool in sysinfo['Pools']:


    if caplen == 1:
        for cap in sysinfo['Capacity Info']:
            usedsize = cap['sizeUsed']
            freesize = cap['sizeFree']
            totalsize = cap['sizeTotal']
            effratio = cap['overallEfficiencyRatio']
            if 'dataReductionRatio' in cap.keys():
                ddr = cap["dataReductionRatio"]
                ddrchk = True
            else:
                ddrchk = False

    if basiclen == 1:
        for sys in sysinfo['Basic']:
            sysname = sys['name']
            sysmodel = sys['model']
            sysswversion = sys['softwareVersion']
    else:
        print('Basic information is greater than 1')
    
    if snlen == 1:
        for sn in sysinfo['SN']:
            syssn = sn['serialNumber']
    else:
        print('Serial Number information is greate than 1')
    

    # for net in sysinfo['Network']:
    #     for value in net.values():
    #         print(value)
    
    title_format = workbook.add_format()
    title_format.set_bold()
    title_format.set_font_size(14)
    title_format2 = workbook.add_format()
    title_format2.set_bold()
    title_format2.set_font_size(14)
    title_format2.set_align('center')
    subtitle_format = workbook.add_format()
    subtitle_format.set_font_size(11)
    subtitle_format.set_align('right')
    subtitle_format.set_bold()
    data_format = workbook.add_format()
    data_format.set_align('center')
    subtitle_format2 = workbook.add_format()
    subtitle_format2.set_bold()
    subtitle_format2.set_align('center')
    subtitle_format.set_font_size(11)
    
    worksheet =  workbook.add_worksheet(sysname)

    worksheet.write("A1", 'System Name', title_format)
    worksheet.write("A2", 'System SN', title_format)
    worksheet.write("A3", 'System Model', title_format)
    worksheet.write("A4", 'System Code Level', title_format)
    worksheet.write("A5", 'Efficiency Ratio', title_format)
    worksheet.write("A6", 'Data Reduction Ratio', title_format)
    worksheet.write("A7", 'Capacity Info', title_format)
    worksheet.write("A8", 'Total (TB)', subtitle_format)
    worksheet.write("A9", 'Used (TB)', subtitle_format)
    worksheet.write("A10",'Free (TB)', subtitle_format)
    worksheet.write("D2", 'Name', subtitle_format2)
    worksheet.write("E2", 'All Flash', subtitle_format2)
    worksheet.write("F2", 'Used', subtitle_format2)
    worksheet.write("G2", 'Free', subtitle_format2)
    worksheet.write("H2", 'Total', subtitle_format2)
    worksheet.merge_range("D1:H1", 'Pools', title_format2)

    worksheet.write("B1", sysname, data_format)
    worksheet.write("B3", sysmodel, data_format)
    worksheet.write("B4", sysswversion, data_format)
    worksheet.write("B2", syssn, data_format)
    worksheet.write("B8", totalsize, data_format)
    worksheet.write("B9", usedsize, data_format)
    worksheet.write("B10", freesize, data_format)
    worksheet.write("B5", effratio, data_format)
    if ddrchk == True:
        worksheet.write("B6", ddr, data_format)
    else:
        worksheet.write("B6", "N/A", data_format)
    
    return

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
    
    poolinfo = session.get('https://' + UnityArr + '/api/types/pool/instances?fields=name,type,isAllFlash,health,sizeTotal,sizeUsed,sizeFree,dataReductionRatio&compact=true', headers={"X-EMC-REST-CLIENT":"true"}, verify=False)
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

unityip = ["10.237.196.48","10.237.196.198"]
workbook = xlsxwriter.Workbook("ConfigBook.xlsx")
for ip in unityip:
    
    UnityCon(ip, workbook)

workbook.close()