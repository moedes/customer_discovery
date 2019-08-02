import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
import creds
from capconverter import convert
import xlsxwriter

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

isisession = requests.Session()
isisession.auth = ('root', 'MRD3nver!')

class IsilonSystem:

    def IsilonGetAZ(self):

        isiazinfo = isisession.get('https://' + self.IsilonArr + ':8080/platform/3/zones', verify=False)

        isiazlst = []

        if isiazinfo.status_code == 200:

            isiazinfo = isiazinfo.json()

            for az in isiazinfo['zones']:

                isiazlst.append(az)

        return isiazlst
    
    def __init__(self, IsilonArr, workbook=None):
        self.IsilonArr = IsilonArr
        self.workbook = workbook

    def IsilonGetLicenseInfo(self):

        isilicinfo = isisession.get('https://' + self.IsilonArr + ':8080/platform/1/license/licenses', verify=False)

        if isilicinfo.status_code == 200:

            isilicinfo = isilicinfo.json()

            isiliclst = []

            for licinfo in isilicinfo['licenses']:

                isiliclst.append(licinfo)
        
        return isiliclst

    def IsilonCloudPools(self):

        isicpinfo = isisession.get('https://' + self.IsilonArr + ':8080/platform/3.1/cloud/pools', verify=False)

        isicpinfolst = []

        if isicpinfo.status_code == 200:
            isicpinfo = isicpinfo.json()
            
            if isicpinfo['total'] > 0:
                
                for cpinfo in isicpinfo['pools']:
                    isicpinfolst.append(cpinfo)
        
        return isicpinfolst
    
    def IsilonGetNFS(self):

        isizoneinfo = isisession.get('https://' + self.IsilonArr + ':8080/platform/3/zones', verify=False).json()
        
        nfsexportlst = []

        for zone in isizoneinfo['zones']:
            zonename = zone['name']
                    
            isinfsshareinfo = isisession.get('https://' + self.IsilonArr + ':8080/platform/4/protocols/nfs/exports?zone=' + zonename, verify=False)
                        
            if isinfsshareinfo.status_code == 200:
                
                isinfsshareinfo = isinfsshareinfo.json()

                if isinfsshareinfo['total'] > 0:
                    
                    for exports in isinfsshareinfo['exports']:
                        nfsexportlst.append(exports)

        return nfsexportlst
    
    def IsilonGetSMB(self):
               
        isizoneinfo = isisession.get('https://' + self.IsilonArr + ':8080/platform/3/zones', verify=False).json()
        
        isismblst = []

        for zone in isizoneinfo['zones']:
            zonename = zone['name']
            isismbshareinfo = isisession.get('https://' + self.IsilonArr + ':8080/platform/7/protocols/smb/shares?zone=' + zonename , verify=False).json()

            if isismbshareinfo['total'] > 0:
            
                for share in isismbshareinfo['shares']:
                    share['zone'] = zonename
                    isismblst.append(share)
        
        return isismblst

    def IsilonGetPools(self):

        isipoolsinfo = isisession.get('https://' + self.IsilonArr + ':8080/platform/3/storagepool/storagepools', verify=False).json()
        
        isipoollst = []

        totalpoolused = 0
        totalpoolfree = 0
        totalpoolavail = 0
        totalpool = 0
        
        for pool in isipoolsinfo['storagepools']:
            isipoollst.append(pool)
            
        print(json.dumps(isipoollst, indent=2)

        return isipoollst

    def IsilonID(self):
        
        isinameinfo = isisession.get('https://' + self.IsilonArr + ':8080/platform/5/cluster/identity', verify=False).json()
        isiname = isinameinfo['name']

        return isiname

    def IsilonGetNodes(self):
        
        isinodeinfo = isisession.get('https://' + self.IsilonArr + ':8080/platform/7/cluster/nodes', verify=False).json()
        
        ssdtotal = 0
        hddtotal = 0
        ssdTB = 0
        hddTB = 0

        arrnodeinfodic = {}
        nodedic = {}

        for node in isinodeinfo['nodes']:
            nodeid = node['lnn']
            newnode = "node" + str(nodeid)
            nodeinfodic = {}
            nodeinfodic['model'] = node['hardware']['model']
            nodeinfodic['sn'] = node['hardware']['serial_number']
            nodeinfodic['version'] = node['status']['release']
            capacity = node['status']['capacity']
            nodeinfodic['product'] = node['hardware']['product']
            for cap in capacity:
                if cap['type'] == 'SSD':
                    ssdcap = cap['bytes']
                    ssdTB = convert.bytestoTB(ssdcap)
                    ssdtotal = ssdtotal + ssdTB
                    nodeinfodic['SSD Capacity'] = ssdTB
                elif cap['type'] == 'HDD':
                    hddcap = cap['bytes']  
                    hddTB = convert.bytestoTB(hddcap)
                    hddtotal = hddtotal + hddTB
                    nodeinfodic['HDD Capacity'] = hddTB
                else:
                    print('Error getting drive type or drive type not found')
            arrnodeinfodic[newnode] = nodeinfodic

        arrnodelst = [arrnodeinfodic]
        nodedic['nodes'] = arrnodelst

                
        if ssdtotal == 0 or hddtotal == 0:
            if ssdtotal == 0:
                print('No SSDs Found')
            else:
                print('No HDDs Found')
        else:
            print('Drives Found')
        
        nodedic['SSD Total'] = round(ssdtotal, 2)
        nodedic['HDD Total'] = round(hddtotal, 2)
        
        return nodedic

    def IsilonCon(self):

        isilonbox = IsilonSystem(self.IsilonArr)

        sysname = isilonbox.IsilonID()
        isilonboxnodes = isilonbox.IsilonGetNodes()
        isilonboxpools = isilonbox.IsilonGetPools()

        print(json.dumps(isilonboxpools, indent=4))
        isilonboxsmb = isilonbox.IsilonGetSMB()
        isilonboxnfs = isilonbox.IsilonGetNFS()
        isilonboxcp = isilonbox.IsilonCloudPools()
        isilonboxlic = isilonbox.IsilonGetLicenseInfo()
        isilonboxaz = isilonbox.IsilonGetAZ()

        title_format = self.workbook.add_format()
        title_format.set_bold()
        title_format2 = self.workbook.add_format()
        title_format2.set_bold()
        title_format2.set_font_size(14)
        title_format2.set_align('center')
        subtitle_format = self.workbook.add_format()
        subtitle_format.set_font_size(11)
        subtitle_format.set_align('right')
        subtitle_format.set_bold()
        data_format = self.workbook.add_format()
        data_format.set_align('center')
        data_format2 = self.workbook.add_format()
        data_format2.set_align('right')
        subtitle_format2 = self.workbook.add_format()
        subtitle_format2.set_bold()
        subtitle_format2.set_align('center')
        subtitle_format.set_font_size(11)

        worksheet =  self.workbook.add_worksheet("Isilon General - " + sysname)
        exportworksheet = self.workbook.add_worksheet("Isilon Exports - " + sysname)

        worksheet.merge_range("B1:F1", "Cluster Name", title_format2)
        worksheet.merge_range("B2:F2", sysname, data_format)
        worksheet.merge_range("B4:F4", "Nodes", title_format2)
        worksheet.write("B5", "Model", subtitle_format2)
        worksheet.write("C5", "Serial Number", subtitle_format2)
        worksheet.write("D5", "Code Version", subtitle_format2)
        worksheet.write("E5", "SSD Capacity (TB)", subtitle_format2)
        worksheet.write("F5", "HDD Capacity (TB)", subtitle_format2) 
        worksheet.merge_range("H1:O1", "Storage Pools", title_format2)
        worksheet.write("H2", "Name", subtitle_format2)
        worksheet.write("I2", "Type", subtitle_format2)
        worksheet.write("J2", "Protect Policy", subtitle_format2)
        worksheet.write("K2", "Nodes", subtitle_format2)
        worksheet.write("L2", "Used (TB)", subtitle_format2)
        worksheet.write("M2", "Free (TB)", subtitle_format2)
        worksheet.write("N2", "Avail (TB)", subtitle_format2)
        worksheet.write("O2", "Total (TB)", subtitle_format2)        

        noderow = 6
        for nodes in isilonboxnodes['nodes']:
            sortnodes = sorted(nodes.items(), key=lambda node: node[1]['model'])  #sorts nodes using anonymous lambda function with index of 1
            for node, nodedict in sortnodes:
                noderowstr = str(noderow)
                model = nodedict['model']
                sn = nodedict['sn']
                swversion = nodedict['version']
                nodessdcap = nodedict['SSD Capacity']
                nodehddcap = nodedict['HDD Capacity']
                worksheet.write("B" + noderowstr, model, data_format)
                worksheet.write("C" + noderowstr, sn, data_format)
                worksheet.write("D" + noderowstr, swversion, data_format)
                worksheet.write("E" + noderowstr, nodessdcap, data_format)
                worksheet.write("F" + noderowstr, nodehddcap, data_format)
                noderow += 1
        
        noderow += 1
        noderowstr = str(noderow)
        ssdtotalcap = isilonboxnodes['SSD Total']
        worksheet.write("C" + noderowstr, "Total SSD Capacity (TB)", subtitle_format2)
        worksheet.write("D" + noderowstr, ssdtotalcap, data_format)
        
        noderow += 1
        noderowstr = str(noderow)
        hddtotalcap = isilonboxnodes['HDD Total']
        worksheet.write("C" + noderowstr, "Total HDD Capacity (TB)", subtitle_format2)
        worksheet.write("D" + noderowstr, hddtotalcap, data_format)

        licrow = noderow + 2
        licrowstr = str(licrow)
        if len(isilonboxlic) > 0:

            worksheet.merge_range("C" + licrowstr + ":E" + licrowstr, "Licenses", title_format2)    
            licrow += 1
            licrowstr = str(licrow)
            worksheet.write("C" + licrowstr, "Name", subtitle_format2)
            worksheet.write("D" + licrowstr, "Status", subtitle_format2)
            worksheet.write("E" + licrowstr, "Duration", subtitle_format2)
            licrow += 1
                        
            for lic in isilonboxlic:

                licrowstr = str(licrow)
                licinfoname = lic['name']
                licinfostatus = lic['status']
                licinfodur = str(lic['duration'])

                worksheet.write("C" + licrowstr, licinfoname, data_format)
                worksheet.write("D" + licrowstr, licinfostatus, data_format)
                worksheet.write("E" + licrowstr, licinfodur, data_format)

                licrow += 1
                
        smbrow = 1
        smbrowstr = str(smbrow)
        if len(isilonboxsmb) > 0:
            
            exportworksheet.merge_range("B" + smbrowstr + ":E" + smbrowstr, "SMB Shares", title_format2)
            smbrow += 1
            smbrowstr = str(smbrow)
            exportworksheet.write("B" + smbrowstr, "Name", subtitle_format2)
            exportworksheet.write("C" + smbrowstr, "Path", subtitle_format2)
            exportworksheet.write("D" + smbrowstr, "Description", subtitle_format2)
            exportworksheet.write("E" + smbrowstr, "Access Zone", subtitle_format2)
            smbrow += 1

            for share in isilonboxsmb:
                smbrowstr = str(smbrow)
                isismbname = share['name']
                isismbpath = share['path']
                isismbdesc = share['description']
                isismbzone = share['zone']
                exportworksheet.write("B" + smbrowstr, isismbname, data_format)
                exportworksheet.write("C" + smbrowstr, isismbpath, data_format)
                exportworksheet.write("D" + smbrowstr, isismbdesc, data_format)
                exportworksheet.write("E" + smbrowstr, isismbzone, data_format)
                smbrow += 1

        nfsrow = 1
        nfsrowstr = str(nfsrow)
        if len(isilonboxnfs) > 0:

            exportworksheet.merge_range("G" + nfsrowstr + ":J" + nfsrowstr, "NFS Exports", title_format2)
            nfsrow += 1
            nfsrowstr = str(nfsrow)
            exportworksheet.write("G" + nfsrowstr, "ID", subtitle_format2)
            exportworksheet.write("H" + nfsrowstr, "Paths", subtitle_format2)
            exportworksheet.write("I" + nfsrowstr, "Description", subtitle_format2)
            exportworksheet.write("J" + nfsrowstr, "Access Zone", subtitle_format2)
            nfsrow += 1

            for export in isilonboxnfs:
                nfsrowstr = str(nfsrow)
                isiexportid = str(export['id'])
                isiexportpaths = str(export['paths']).strip('[]')
                isiexportzone = export['zone']
                isiexportdesc = export['description']
                exportworksheet.write("G" + nfsrowstr, isiexportid, data_format)
                exportworksheet.write("H" + nfsrowstr, isiexportpaths, data_format)
                exportworksheet.write("I" + nfsrowstr, isiexportdesc, data_format)
                exportworksheet.write("J" + nfsrowstr, isiexportzone, data_format)
                nfsrow += 1
        
        poolrow = 3
        for pool in isilonboxpools:
            poolrowstr = str(poolrow)
            isipoolname = pool['name']
            isipoollnn = str(pool['lnns']).strip('[]')
            isipooltype = pool['type']
            isipoolprotect = pool['protection_policy']
            isipoolusedt = pool['usage']['used_bytes']
            isipoolusedtint = convert.bytestoTB(int(isipoolusedt))
            isipoolfreet = pool['usage']['free_bytes']
            isipoolfreetint = convert.bytestoTB(int(isipoolfreet))
            isipooltotal = pool['usage']['total_bytes']
            isipooltotalint = convert.bytestoTB(int(isipooltotal))
            isipoolavail = pool['usage']['avail_bytes']
            isipoolavailint = convert.bytestoTB(int(isipoolavail))
            worksheet.write("H" + poolrowstr, isipoolname, data_format)
            worksheet.write("I" + poolrowstr, isipooltype, data_format)
            worksheet.write("J" + poolrowstr, isipoolprotect, data_format)
            worksheet.write("K" + poolrowstr, isipoollnn, data_format)
            worksheet.write("L" + poolrowstr, isipoolusedtint, data_format)
            worksheet.write("M" + poolrowstr, isipoolfreetint, data_format)
            worksheet.write("N" + poolrowstr, isipoolavailint, data_format)
            worksheet.write("O" + poolrowstr, isipooltotalint, data_format)
            poolrow += 1

        cprow = poolrow + 1
        cprowstr = str(cprow)
        if len(isilonboxcp) > 0:

            worksheet.merge_range("H" + cprowstr + ":K" + cprowstr, "Cloud Pools", title_format2)
            cprow += 1
            cprowstr = str(cprow)
            worksheet.write("H" + cprowstr, "Name", subtitle_format2)
            worksheet.write("I" + cprowstr, "Description", subtitle_format2)
            worksheet.write("J" + cprowstr, "State", subtitle_format2)
            worksheet.write("K" + cprowstr, "Type", subtitle_format2)
            cprow += 1

            for cp in isilonboxcp:
                cprowstr = str(cprow)
                cpname = cp['name']
                cpdesc = cp['description']
                cpstate = cp['state']
                cptype = cp['type']
                worksheet.write("H" + cprowstr, cpname, data_format)
                worksheet.write("I" + cprowstr, cpdesc, data_format)
                worksheet.write("J" + cprowstr, cpstate, data_format)
                worksheet.write("K" + cprowstr, cptype, data_format)
                cprow += 1
        
        azrow = poolrow + 1
        azrowstr = str(azrow)

        if len(isilonboxaz) > 0:

            worksheet.merge_range("M" + azrowstr + ":N" + azrowstr, "Access Zones", title_format2)
            azrow += 1
            azrowstr = str(azrow)

            worksheet.write("M" + azrowstr, "Name", subtitle_format2)
            worksheet.write("N" + azrowstr, "Path", subtitle_format2)

            azrow += 1

            for az in isilonboxaz:
                
                azrowstr = str(azrow)
                azname = az['name']
                azpath = az['path']
                worksheet.write("M" + azrowstr, azname, data_format)  
                worksheet.write("N" + azrowstr, azpath, data_format) 

                azrow += 1         
        