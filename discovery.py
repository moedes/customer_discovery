import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
import creds
import pandas as pd
import xlsxwriter
import unity
from storops import VNXSystem

session = requests.Session()
session.auth = (creds.unitylogin["username"], creds.unitylogin["password"])

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def SystemCon(SysArr, workbook):

    sysinfo = {}    

    unitybox = unity.UnitySystem(SysArr)
  
    sysinfo['Basic'] = unitybox.GetUnityBasic()
    sysinfo['Network'] = unitybox.GetUnityPorts()
    sysinfo['Pools'] = unitybox.GetUnityPools()
    sysinfo['Software'] = unitybox.GetUnitySWInfo()
    sysinfo['SN'] = unitybox.GetUnitySNInfo()
    sysinfo['Capacity Info'] = unitybox.GetUnitySysCap()
    sysinfo['Filesystem'] = unitybox.GetUnityFSInfo()
    
    #print(len(sysinfo['Filesystem']))

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
    data_format2 = workbook.add_format()
    data_format2.set_align('right')
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
    worksheet.write("A12", 'Filesystems', title_format)
    worksheet.write("A13", "FS Name", subtitle_format)
    worksheet.write("B13", "Pool", subtitle_format2)
    worksheet.write("C13", "NAS Server", subtitle_format2)
    worksheet.write("D13", "Shares", subtitle_format2)
    worksheet.write("E13", "Exports", subtitle_format2)
    worksheet.write("F13", "FS Type", subtitle_format2)
    worksheet.write("G13", "Used (TB)", subtitle_format2)
    worksheet.write("H13", "Total (TB)", subtitle_format2)
    worksheet.write("I13", "Allocated (TB)", subtitle_format2)
    worksheet.write("J13", "Total Allocated (TB)", subtitle_format2)
    worksheet.write("D2", 'Pool Name', subtitle_format2)
    worksheet.write("E2", 'All Flash', subtitle_format2)
    worksheet.write("F2", 'Used (TB)', subtitle_format2)
    worksheet.write("G2", 'Free (TB)', subtitle_format2)
    worksheet.write("H2", 'Total (TB)', subtitle_format2)
    worksheet.write("I2", "Percent Free", subtitle_format2)
    worksheet.merge_range("D1:I1", 'Pools', title_format2)

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
    
    if poollen > 0:
        poolrow = 3
        for pool in sysinfo['Pools']:
            poolname = pool['name']
            poolfreesize = pool['sizeFree']
            poolusedsize = pool['sizeUsed']
            pooltotalsize = pool['sizeTotal']
            poolisaf = pool['isAllFlash']
            poolpctfree = pool['Percent Free']
            poolrowstr = str(poolrow)
            worksheet.write("D" + poolrowstr, poolname, data_format)
            worksheet.write("E" + poolrowstr, poolisaf, data_format)
            worksheet.write("F" + poolrowstr, poolusedsize, data_format)
            worksheet.write("G" + poolrowstr, poolfreesize, data_format)
            worksheet.write("H" + poolrowstr, pooltotalsize, data_format)
            worksheet.write("I" + poolrowstr, poolpctfree, data_format)
            poolrow = poolrow + 1
    else:
        poolrowstr = str(poolrow)
        poolname = "No Pool Information"
        worksheet.write("D" + poolrowstr, poolname, data_format)
        
    
    fsrow = 14
    fsrowstr = str(fsrow)
    for fs in sysinfo['Filesystem']:
        fsname = fs['name']
        nasserver = fs['nasServer']['name']
        fspool = fs['pool']['name']
        fsallocated = fs['sizeAllocated']
        fstotalallocated = fs['sizeAllocatedTotal']
        fsused = fs['sizeUsed']
        fstotal = fs['sizeTotal']
        fstype = fs['type']
        worksheet.write("A" + fsrowstr, fsname, data_format2)
        worksheet.write("B" + fsrowstr, fspool, data_format)
        worksheet.write("C" + fsrowstr, nasserver, data_format)
        worksheet.write("F" + fsrowstr, fstype, data_format)
        worksheet.write("G" + fsrowstr, fsused, data_format)
        worksheet.write("H" + fsrowstr, fstotal, data_format)
        worksheet.write("I" + fsrowstr, fsallocated, data_format)
        worksheet.write("J" + fsrowstr, fstotalallocated, data_format)
        if 'cifsShare' in fs.keys():
            for share in fs['cifsShare']:
                cifsrow = fsrow
                cifsrowstr = str(cifsrow)
                sharename = share['name']
                worksheet.write("D" + fsrowstr, sharename, data_format)
                exports = share['exportPaths']
                if len(exports) > 1:
                    for export in exports:
                        worksheet.write("E" + cifsrowstr, export, data_format)
                        cifsrow = cifsrow + 1    
                        cifsrowstr = str(cifsrow)           
                if cifsrow > fsrow:
                    fsrow = cifsrow
                    fsrowstr = str(fsrow)
                else:
                    fsrow = fsrow + 1
                    fsrowstr = str(fsrow)

        if 'nfsShare' in fs.keys():
            for nfs in fs['nfsShare']:
                nfsrow = fsrow
                nfsrowstr = str(nfsrow)
                nfssharename = nfs['name']
                worksheet.write("D" + fsrowstr, nfssharename, data_format)
                nfsexports = nfs['exportPaths']
                if len(nfsexports) > 1:
                    for nfsexport in nfsexports:
                        worksheet.write("E" + nfsrowstr, nfsexport, data_format)
                        nfsrow = nfsrow + 1    
                        nfsrowstr = str(nfsrow)
                else:
                    for nfsexport in nfsexports:
                        worksheet.write("E" + fsrowstr, nfsexport, data_format)      
                
                if nfsrow > fsrow:
                    fsrow = nfsrow
                    fsrowstr = str(fsrow)
                else:
                    fsrow = fsrow + 1
                    fsrowstr = str(fsrow)
            
    return

vnx = VNXSystem('10.237.196.160', 'sysadmin', 'sysadmin')

unityip = ["10.237.196.48", "10.237.196.198"]
workbook = xlsxwriter.Workbook("ConfigBook.xlsx")
for ip in unityip:
    
    SystemCon(ip, workbook)

workbook.close()