from datetime import date, timedelta, datetime
import requests
print("running")
day_arr = [1,3,7,14,28]
for num in day_arr:
    response = requests.request("GET", 'https://inventory.jkwenterprises.com/updatedb/%d' % num)
    print('done | ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") )
response = requests.request("GET", 'https://inventory.jkwenterprises.com/emailnotifications')
