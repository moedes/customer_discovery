import xlsxwriter
import unity
from storops import VNXSystem

vnx = VNXSystem('10.237.196.160', 'sysadmin', 'sysadmin')

unityip = ["10.237.196.48", "10.237.196.198"]
workbook = xlsxwriter.Workbook("ConfigBook.xlsx")
for ip in unityip:
    
    unitybox = unity.UnitySystem(ip, workbook)
    unitybox.UnitySystemCon()

workbook.close()