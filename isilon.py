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

    def __init__(self, IsilonArr, workbook=None):
        self.IsilonArr = IsilonArr
        self.workbook = workbook

    def IsilonGetNFS(self):

        isinfsshareinfo = isisession.get('https://' + self.IsilonArr + ':8080/platform/4/protocols/nfs/exports', verify=False)

        if isinfsshareinfo.status_code == 200:
            nfsexportlst = []
            isinfsshareinfo = isinfsshareinfo.json()

            if isinfsshareinfo['total'] > 0:

                for exports in isinfsshareinfo['exports']:
                    nfsexportlst.append(exports)
        else:
            nfsexportlst = []

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
        
        for pool in isipoolsinfo['storagepools']:
            isipoollst.append(pool)
        
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
        isilonboxsmb = isilonbox.IsilonGetSMB()
        isilonboxnfs = isilonbox.IsilonGetNFS()

        for smb in isilonboxsmb:
            print(smb['name'] + " " + smb['zone'])

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
                exportworksheet.write("C" + smbrowstr, isismbname, data_format)
                exportworksheet.write("D" + smbrowstr, isismbpath, data_format)
                exportworksheet.write("E" + smbrowstr, isismbdesc, data_format)
                exportworksheet.write("F" + smbrowstr, isismbzone, data_format)
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
                exportworksheet.write("H" + nfsrowstr, isiexportid, data_format)
                exportworksheet.write("I" + nfsrowstr, isiexportpaths, data_format)
                exportworksheet.write("J" + nfsrowstr, isiexportdesc, data_format)
                exportworksheet.write("K" + nfsrowstr, isiexportzone, data_format)
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
                
        


                   
