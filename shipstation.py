from flask import Blueprint, request
from databases.models import shipstationAddresses
import requests
import dropbox
import csv
import os
import json
import pandas as pd
from datetime import date, datetime

from appdb import  db

# Blueprint Configuration
ss_bp = Blueprint('ssaddresses_bp', __name__,
                    template_folder='assets/templates',
                    static_folder='assets')

@ss_bp.route('/webhook/shipstation/validation', methods=['POST'])
def ss_webhook():
    foo = request.get_data()
    data = json.loads(foo)


    url = data['resource_url']

    payload = {}
    headers = {
      'Authorization': 'Basic NGQyMmJhYWI0NjlmNDlhNzk0ZjhmMzAwMmI3NTZjMGE6ODc5NDkyYjlhNTBhNGZmYTkyM2E5ZjI2NzY0OTYwZmE='
    }

    response = requests.request("GET", url, headers=headers, data = payload)

    data = response.text.encode('utf8')

    json_data = json.loads(data)
    total_orders = json_data['total']
    data_dicts=[]
    for order in range(total_orders):
        if json_data['orders'][order]['shipTo']['addressVerified'] != "Address validated successfully":
            orderNumber = json_data['orders'][order]['orderNumber']
            customerEmail = json_data['orders'][order]['customerEmail']
            name = json_data['orders'][order]['shipTo']['name']
            try:
                data_dicts.append({'orderNumber' : orderNumber, "name": name, "email": customerEmail})
                log = shipstationAddresses(name = name, customer_email = customerEmail, order_number = orderNumber )
                db.session.add(log)
                db.session.commit()
            except Exception as ex:
                return (str(ex), 'hi')

    address_csv = "Invalidated Addresses.csv"
    here = os.path.dirname(os.path.abspath(__file__))
    ss_csv = os.path.join(here,address_csv)
    time = datetime.now().strftime("%B %d, %Y, %Hhr %Mmin %Ssec")
    today = date.today()
    weekday = today.weekday()

    if (weekday):

        dbx = dropbox.Dropbox('81NCrijVuKMAAAAAAAAAAdL-1URD2nif2sJUKDq06k_l4VPVUp_ETOkKAKzk7vOl')
        with open(ss_csv, 'w+') as f:
            out = csv.writer(f)
            out.writerow(['Order Number', 'Email', 'Name'])
            #for item in db.session.query(shipstationAddresses).all():
            for item in data_dicts:
                out.writerow([item['orderNumber'], item['email'], item['name']])
            f.close()
        df = pd.read_csv(ss_csv)
        if df.empty:
            return('No Invalid Addresses Found')
        with open(ss_csv,"rb") as f:
                 # upload gives you metadata about the file
                 # we want to overwite any previous version of the file
            dbx.files_upload(f.read(), f'/Invalidated Shipstation Addresses/SS Addresses {time}.csv', mode=dropbox.files.WriteMode("overwrite"))
    return('Success', 200)
