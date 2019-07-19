import xlsxwriter
import unity
import isilon
from storops import VNXSystem

#vnx = VNXSystem('10.237.196.160', 'sysadmin', 'sysadmin')

unityip = ["10.237.196.48", "10.237.196.198"]
isilonip = ['10.237.194.43']
workbook = xlsxwriter.Workbook("ConfigBook.xlsx")

for ip in unityip:
    
    unitybox = unity.UnitySystem(ip, workbook)
    unitybox.UnitySystemCon()

for ip in isilonip:
    
    isilonbox = isilon.IsilonSystem(ip, workbook)
    isilonbox.IsilonCon()

workbook.close()