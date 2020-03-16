from sqlalchemy import Column, Integer,Unicode, Boolean
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium import webdriver
import time
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from flask import jsonify
from twilio.rest import Client



class Funnel_info:
	def __init__(self, funnel_name, link):
		self.funnel_name = funnel_name
		self.link = link




BaseModel = declarative_base()

class Funnels(BaseModel):
    """Model for the stations table"""
    __tablename__ = 'funnel_identities'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key = True)
    funnel_name = Column(Unicode)
    funnel_id = Column(Unicode)
    view_id = Column(Unicode)
    stats_link = Column(Unicode)
    optin = Column(Unicode)

    @property
    def serialize(self):
       """Return object data in easily serializable format"""
       return {
           'id': self.id,
           'funnel_name': self.funnel_name,
           'funnel_id': self.funnel_sku,
           # This is an example how to deal with Many2Many relations
           'view_id': self.view_id,
           'stats_link' : self.stats_link,
           'optin' : self.optin

       }

       def __init__(self, funnel_name,funnel_id, view_id, optin, stats_link):
           self.id = id
           self.funnel_name = funnel_name
           self.funnel_id = funnel_id
           self.view_id = view_id
           self.stats_link = stats_link
           self.optin = optin


class Notifs(BaseModel):

    __tablename__='notif_settings'
    __table_args__ = {'extend_existing': True}


    id = Column(Integer, primary_key = True)
    funnel_name = Column(Unicode)
    sms = Column(Boolean)
    email = Column(Boolean)






def send_email(new_arr):

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
            for item in new_arr:
                body_string += ' Funnel: %s is down.  Go here to check: %s' %  (item['funnel_name'], item['link'])
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
                             body=body_string,
                             from_='+14056228386',
                             to=number
                         )

            print(message.sid)

        else:
            pass


    print(new_arr)


print('start')
engine = create_engine('postgresql+psycopg2://jkwuser:a-nice-random-password@10.0.0.46:11366/skudb')
Session = sessionmaker(bind=engine)
session = Session()
p_skus = session.query(Funnels).all()
array_funnels = []


    # we can now start Firefox and it will run inside the virtual display
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
browser = webdriver.Chrome(options = chrome_options)


for i in p_skus:
    if i.optin == 'https://patpubs.clickfunnels.com/trump-maga-hat-f-s-offer676769':
        browser.get(i.optin)
        time.sleep(1)
        if 'https://patpubs.clickfunnels.com/nopage_error.html' == browser.current_url:
            funnel_class = Funnel_info(i.funnel_name, i.optin)
            array_funnels.append(funnel_class.__dict__)

if array_funnels is not []:
    print(array_funnels)
    send_email(array_funnels)

browser.quit()

print('success')









