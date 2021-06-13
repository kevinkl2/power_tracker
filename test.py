from pyHS100 import SmartPlug
from pyHS100 import Discover
from os import system, name, getenv
from pprint import pformat as pf
import csv
import datetime
import time
import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

#sheet.append_row(row)

def clear():   
    if name == 'nt': 
        _ = system('cls') 
    else: 
        _ = system('clear')

# for dev in Discover.discover().values():
#     print(dev)

load_dotenv()

plug = SmartPlug(getenv("IP"))
print(plug.get_emeter_daily(year=2021, month=5))
print(sum(plug.get_emeter_daily(year=2021, month=5).values()))

# while True:
#     try:
#         clear()
#         currentDT = datetime.datetime.now();
#         print("{} watts".format(plug.get_emeter_realtime()["power"]))
#         hours = currentDT.hour + (currentDT.minute/60) + (currentDT.second/3600)
#         kwh = plug.get_emeter_daily(year=currentDT.year, month=currentDT.month)[currentDT.day]
#         print("{} kwh".format(kwh))
#         print("{:.2f} watts".format(kwh/hours*1000))
#         time.sleep(1)
#     except Exception as e:
#         print(e)

# while (True):
#     sheet = None
#     try:
#         creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
#         client = gspread.authorize(creds)
#         sheet = client.open("Power").get_worksheet(2)
#         data = dict()
#         currentDT = datetime.datetime.now()
#         data['date'] = "{}-{}-{}".format(currentDT.year,currentDT.month,currentDT.day)
#         data['time'] = "{}:{}:{}.{}".format(currentDT.hour,currentDT.minute,currentDT.second,currentDT.microsecond)
#         data.update(plug.get_emeter_realtime())
#         data['dayuse'] = plug.get_emeter_daily(year=currentDT.year, month=currentDT.month)[currentDT.day]

#         row = [data[i] for i in data]
#         #sheet.append_row(row)
        
#         sheet.append_row(row)
#         print("success")
#         print(row)
#     except Exception as e:
#         print(e)
#         print("fail")
#     time.sleep(2)