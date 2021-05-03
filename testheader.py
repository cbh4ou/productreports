from datetime import datetime
import pandas as pd
import requests
import os
import shopify
import time

here = os.path.dirname(os.path.abspath(__file__))
f_name = 'Clickbank '+ datetime.today().strftime('%Y-%m-%d') + '.csv'
csv_clickbank = os.path.join(here,f_name)
df = pd.read_csv(csv_clickbank)
df_clickbank = df[df["Order - Number"].str.contains('PPP') == False]
df_shopify = df[df["Order - Number"].str.contains('PPP') == True]


for index, row in df_clickbank.iterrows():
        order = row['Order - Number']
        tracking = row['Shipment - Tracking Number']
        date = row['Date - Shipped Date']
        date = datetime.strptime(date, '%m/%d/%Y %I:%M:%S %p').date()
        date = date.strftime("%Y-%m-%d")

        url = f'https://api.clickbank.com/rest/1.3/shipping2/shipnotice/{order}'

        payload={'fillOrder': 'true' ,
                'date' : date ,
                'carrier':'USPS',
                'tracking': tracking}
        headers = {
        'Authorization': 'DEV-HFD0TSB0UNFCJLB9B04VNFNFCS2LHDRE:API-9DS2Q8EOF2AH5BON282VM5C2N7G5M0S2',
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, params=payload)

        print(response.text)
"""
for index, row in df_shopify.iterrows():
    time.sleep(.5)
    shop_url = 'https://ac6fddca7d5f697f5dd76c1cf09edb9d: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@patriot-powered-products.myshopify.com'
    api_version = '2021-01'
    private_app_password = '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'

    session = shopify.Session(shop_url, api_version, private_app_password)
    shopify.ShopifyResource.activate_session(session)

    page = shopify.Order.find(name='#'+ row['Order - Number'])
    order_id = None
    try:
        order_id = page[0]
    except IndexError:
        continue
    print(order_id.id)
    fulfillment = shopify.Fulfillment({
                    'order_id':order_id.id,
                    'location_id':'5766185019'
                    })

    fulfillment.tracking_company = 'USPS'
    fulfillment.tracking_number = row['Shipment - Tracking Number']
    fulfillment.tracking_url = ''
    fulfillment.notify_customer = True
    fulfillment.save()

    shopify.ShopifyResource.clear_session()
"""
csv_clickbank = os.path.join(here, f_name)
if os.path.exists(csv_clickbank):
    os.remove(csv_clickbank)


