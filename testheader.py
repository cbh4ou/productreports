import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium import webdriver
import time
from twilio.rest import Client
from databases.models  import  Funnels, Notifs, Parentsku
from flask import jsonify
from datetime import datetime
import pandas as pd

class Funnel_info:
	def __init__(self, funnel_name, link):
		self.funnel_name = funnel_name
		self.link = link



def send_alert(new_arr):
    for item in new_arr:
        notif = Notifs.query.filter(Notifs.funnel_name==item).first()
        if notif.email:
            sender_email = "cbh4ou@gmail.com"
            receiver_email = ["connor@jkwenterprises.com", "zach@jkwenterprises.com", "logan@jkwenterprises.com", "jake@jkwenterprises.com", "scott@jkwenterprises.com", "jason@jkwenterprises.com"]
            password = "doabynovtpdoudwz"

            message = MIMEMultipart("alternative")
            message["Subject"] = "Funnel Monitor Report"
            message["From"] = sender_email
            message["To"] = ", ".join(receiver_email)

            # Create the plain-text and HTML version of your message
            text = """\
            Hi,
            How are you?
            Real Python has many great tutorials:
            www.realpython.com"""
            final_string = ''
            final_string += """\

                <p> ***<a href=%s>%s</a>*** : is currently down </p>
            """ % (item['link'], item['funnel_name'])

            html = """\
            <html>
                <body>
                <h4>Funnels Down<h4/>
                %s

                </body>
            </html>
            """ % final_string

            # Turn these into plain/html MIMEText objects
            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")

            # Add HTML/plain-text parts to MIMEMultipart message
            # The email client will try to render the last part first
            message.attach(part1)
            message.attach(part2)

            # Create secure connection with server and send email
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", context=context) as server:
                server.login(sender_email, password)
                server.sendmail(
                    sender_email, receiver_email, message.as_string()
                )
            body_string = ''
            sms_string = ''
            for item in new_arr:
                body_string += ' Funnel: %s is down.  Go here to check: %s' %  (item['funnel_name'], item['link'])
                sms_string += '\nFunnel: %s is down.  Go here to check: %s' %  (item['funnel_name'], item['link'])
            else:
                pass
            if notif.sms:
                account_sid = 'ACd654cc97633bc7ffe43212e705370d84'
                auth_token = '410753a8ec99c382fb743342c05bcd1e'
                client = Client(account_sid, auth_token)
                numbers_to_message = ['+14052070115', '+19185778827', '+14052068053']
                for number in numbers_to_message:
                    message = client.messages \
                        .create(
                                body=sms_string,
                                from_='+14056228386',
                                to=number
                                 )

                    print(message.sid)

                else:
                    pass


        print(new_arr)


print('start')


p_skus = Funnels.query.all()
array_funnels = []


    # we can now start Firefox and it will run inside the virtual display
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
browser = webdriver.Chrome(options = chrome_options)


for i in p_skus:
    browser.get(i.optin)
    time.sleep(1)
    if 'https://patpubs.clickfunnels.com/nopage_error.html' == browser.current_url:
            funnel_class = Funnel_info(i.funnel_name, i.optin)
            array_funnels.append(funnel_class.__dict__)

if array_funnels is not []:
    print(array_funnels)
    send_alert(array_funnels)

browser.quit()

print('success')



def testdb():
    sku_names = []
    sku_percent_left = []
    inbound = []
    all_skus = Parentsku.query().all()
    tt = pd.read_csv('/home/jkwent/productreports/your_csv.csv', delimiter=',')
    item_arr = []
    for index, row in tt.iterrows():
        item_arr.append(row['Sku Name'])
    for sku in all_skus:
        if sku != None:
            sku_avg = (sku.day3 * 4.6667 + sku.day7 * 2 + sku.day14 + sku.day28 /2) / 4
            if sku.encorestock != None and sku.encorestock != 0 and sku_avg/sku.encorestock >= .75:
                sku_names.append(sku.parent_sku)
                sku_percent_left.append((sku_avg/sku.encorestock))
                if sku.inboundstock > 0:
                    inbound.append("Awaiting Arrival")
                else:
                    inbound.append("REORDER NOW: Only %f%s of stock left" % ((1 -(sku_avg/sku.encorestock)) * 100, "%"))
    df = pd.DataFrame({'Sku Name':sku_names,
                   'Stock Level Percent':sku_percent_left,
                   'Inbound':inbound,
                   'Time': datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}, columns= ['Sku Name', 'Stock Level Percent', 'Inbound', 'Time'])


    df.to_csv('/home/jkwent/productreports/your_csv.csv', index=False)

    new_arr = []
    for x in range(len(sku_names)):
        if sku_names[x] not in item_arr:
            new_arr.append({'SKU': sku_names[x], 'Inbound': inbound[x] })

    if new_arr:
        sender_email = "connor@jkwenterprises.com"
        receiver_email = ["connor@jkwenterprises.com", "zach@jkwenterprises.com", "scott@jkwenterprises.com"]
        password = "Primussucks72!"

        message = MIMEMultipart("alternative")
        message["Subject"] = "New Stock Alert"
        message["From"] = sender_email
        message["To"] = ", ".join(receiver_email)

        # Create the plain-text and HTML version of your message
        text = """\
        Hi,
        How are you?
        Real Python has many great tutorials:
        www.realpython.com"""
        final_string = ""
        for item in new_arr:
            final_string += """\

            <p> ***%s*** : %s </p>
        """ % (item['SKU'],item['Inbound'])



        html = """\
        <html>
          <body>
            <h4>Critical Stock Levels<h4/>

            %s
            <br>
            <a href="https://inventory.jkwenterprises.com/">Click to go to Inventory Tracker</a>
          </body>
        </html>
        """ % final_string

        # Turn these into plain/html MIMEText objects
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

        # Add HTML/plain-text parts to MIMEMultipart message
        # The email client will try to render the last part first
        message.attach(part1)
        message.attach(part2)

        # Create secure connection with server and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", context=context) as server:
            server.login(sender_email, password)
            server.sendmail(
                sender_email, receiver_email, message.as_string()
            )




    return jsonify(new_arr)





