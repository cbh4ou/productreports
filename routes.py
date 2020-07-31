"""Routes for logged-in application."""
from flask import Blueprint,  redirect, jsonify, request, render_template
from datetime import date, timedelta, datetime
from databases.models import Funnels, Sku, Parentsku, Quantities, Sales, Emails, Contacts, Notifs
import smtplib, ssl
from email.mime.text import MIMEText
import json
from email.mime.multipart import MIMEMultipart
import pandas as pd
from decimal import Decimal

from appdb import app, db

# Blueprint Configuration
main_bp = Blueprint('main_bp', __name__,
                    template_folder='assets/templates',
                    static_folder='assets')



@main_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """Serve logged in Dashboard."""
    return redirect("/")
    """
    return render_template('dashboard.html',
                           title='Flask-Login Tutorial.',
                           template='dashboard-template',
                           current_user=current_user,
                           body="You are now logged in!")
    """


@main_bp.route('/funnel-notifs', methods=['GET'])
def funnel_alerts():
    """Serve logged in Dashboard."""
    return render_template("notifications_fe.html")


@main_bp.route('/json/parentsku', methods=['GET'])
def dropdownjson():
    p_skus = db.session.query(Parentsku).all()
    arr_skus = []
    for i in p_skus:
        if i.parent_sku != None:
            arr_skus.append(i.parent_sku)
    dropdown_object = []
    for sku in range(len(arr_skus)):
        item = dropdown_items(sku+1, arr_skus[sku])
        dropdown_object.append(item.asdict())

    return jsonify(dropdown_object)



class dropdown_items():

    def __init__(self, id, name):
        self.id = id
        self.name = name


    def asdict(self):
        return {'id': self.id, 'name': self.name}


@main_bp.route('/updatedb/<days>', methods=['GET'])
def update_db(days):
    days = int(days)
    parent_skus_arr = []
    featured_skus = db.session.query(Parentsku).all()
    for i in featured_skus:
        parent_skus_arr.append(i.parent_sku)
    parent_final = list(dict.fromkeys(parent_skus_arr))


    quantity = []
    start_date = date.today()
    end_date = date.today()
    word = None
    if days != 1:
        start_date = date.today() - timedelta(days=1)
        end_date = date.today() - timedelta(days=days)
        word = (db.session.query(Sku, Parentsku, Quantities)
            .join(Quantities, Quantities.child_sku == Sku.sku)
            .join(Parentsku)
            .filter(Sku.order_date <= start_date, Sku.order_date >= end_date)
            .all())

        # Set of arrays to pass back to Dataframe Table

    else:
        # Query Table Join
        word = (db.session.query(Sku, Parentsku, Quantities)
            .join(Quantities, Quantities.child_sku == Sku.sku)
            .join(Parentsku)
            .filter(Sku.order_date == start_date)
            .all())

    for index_range in range(len(parent_final)):
            quantity.append(0)

    for psku in parent_final:
        for i in word:
            if i.Parentsku.parent_sku == psku:
                quantity[parent_final.index(psku)] = quantity[parent_final.index(psku)] + i.Quantities.quantity
        new_quant = db.session.query(Parentsku).filter(Parentsku.parent_sku == psku).first()
        if days == 1:
            new_quant.day1 = quantity[parent_final.index(psku)]
            db.session.commit()
        if days == 3:
            new_quant.day3 = quantity[parent_final.index(psku)]
            db.session.commit()
        if days == 7:
            new_quant.day7 = quantity[parent_final.index(psku)]
            db.session.commit()
        if days == 14:
            new_quant.day14 = quantity[parent_final.index(psku)]
            db.session.commit()
        if days == 28:
            new_quant.day28 = quantity[parent_final.index(psku)]
            db.session.commit()


    return  jsonify(dict(zip(parent_final, quantity)))








@main_bp.route('/emailnotifications', methods=['GET'])
def testdb():
    sku_names = []
    sku_percent_left = []
    inbound = []
    all_skus = db.session.query(Parentsku).all()
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
        receiver_email = ["connor@jkwenterprises.com", "zach@jkwenterprises.com", "logan@jkwenterprises.com", "jake@jkwenterprises.com", "scott@jkwenterprises.com", "jason@jkwenterprises.com"]
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




@main_bp.route('/cfwebhook', methods=['POST'])
def receive_item():
    foo = request.get_data()
    data = json.loads(foo)
    order = data["id"]

    if 'error_message' in data:
        if data['error_message'] is None and data["products"] is not None:
            for each in data["products"]:
                order = combine_orders(data['contact']["email"],data["created_at"], order, data['funnel_id'])
                price = each['amount']['fractional']
                new_sku = Sales(order_id=order, email=data['contact']["email"],
                time_created=data["created_at"], funnel_id = data['funnel_id'], product_name=each['name'],
                price=Decimal(price.replace(',',''))/100, product_id=each["id"])
                db.session.add(new_sku)
                db.session.commit()
        else:
            return jsonify("Card Declined"),200

    else:
        question = None
        answer= None
        for key in data:
            if 'question' in key:
                question = data[key]
            if 'answer' in key and data[key]:
                answer = data[key]
        if question is None:
            return jsonify("We only accept first Funnel Steps"),500
        email_type = False
        if data['event'] is 'updated':
            email_type = True
        new_sku =  Emails(email = data['email'], funnel_id = data['funnel_id'],time_created = data["created_at"], updated = email_type, question = question, answer = answer )
        db.session.add(new_sku)
        db.session.commit()

    return jsonify(data["created_at"]),200


def combine_orders(contact, timerange, order, funnel):
    newtimerange = datetime.strptime(timerange, "%Y-%m-%dT%H:%M:%S.000Z")
    newtimerange = newtimerange - timedelta(hours=0, minutes=5)
    orders = db.session.query(Sales).filter(Sales.time_created <= timerange , Sales.time_created >= newtimerange, Sales.email == contact, Sales.funnel_id == str(funnel)).first()
    if orders == None:
        return order
    else:
        return orders.order_id



class notif_item():

    def __init__(self, row, name):
        self.id = row
        self.name = name

@main_bp.route('/funnels/names', methods=['GET', 'POST'])
def send_notifs():
    if request.method == 'GET':
        funnels = (db.session.query(Funnels, Notifs)
            .join(Notifs, Notifs.funnel_name == Funnels.funnel_name)
            .all())
        dropdown_object = []
        num = 0
        for i in funnels:
            num=num+1
            dropdown_object.append(notif_item(num, i.Funnels.funnel_name).__dict__)

        return jsonify(dropdown_object)
    else:
        resp = request.get_json()
        notif = Notifs.query.filter(Notifs.funnel_name==resp['funnel']).first()
        funnels = Funnels.query.filter(Funnels.funnel_name==resp['funnel']).first()
        return {'funnelid' : funnels.funnel_id, 'ga-tag':funnels.view_id, 'landingpage':funnels.optin, 'email' : notif.email, 'sms' : notif.sms}, 200



@main_bp.route('/cfwebhook/funnel_webhooks/test', methods=['POST'])
def cf_webhook():

    return jsonify('success'),200


@main_bp.route('/funnel_webhooks/test', methods=['POST'])
def cf_webhooks():

    return jsonify('success'),200




@main_bp.route('/funnel/edit/<action>', methods=['GET', 'POST'])
def edit_funnels(action):
    if request.method == 'GET':
        funnels = (db.session.query(Funnels, Notifs)
            .join(Notifs, Notifs.funnel_name == Funnels.funnel_name)
            .all())
        dropdown_object = []
        num = 0
        for i in funnels:
            num=num+1
            dropdown_object.append(notif_item(num, i.Funnels.funnel_name,i.Notifs.email, i.Notifs.sms).__dict__)

        return jsonify(dropdown_object)
    else:
        funnel_object = request.get_json()
        if action == 'update':
            if funnel_object['funnelname'] == 'none':
                funnel = Funnels(funnel_name = funnel_object['newfunnel'], view_id= funnel_object['gatag'],
                optin = funnel_object['landingpage'], funnel_id = funnel_object['funnelid'])
                db.session.add(funnel)
                notif = Notifs(funnel_name = funnel_object['newfunnel'],sms = funnel_object['sms'], email = funnel_object['email'])
                db.session.add(notif)
                db.session.commit()
            else:
                funnel = Funnels.query.filter(Funnels.funnel_name== funnel_object['funnelname']).first()
                funnel.funnel_name = funnel_object['newfunnel']
                funnel.view_id = funnel_object['gatag']
                funnel.optin = funnel_object['landingpage']
                funnel.funnel_id = funnel_object['funnelid']
                db.session.commit()
                notif = Notifs.query.filter(Notifs.funnel_name== funnel_object['funnelname']).first()
                notif.funnel_name = funnel_object['newfunnel']
                notif.sms = funnel_object['sms']
                notif.email = funnel_object['email']
                db.session.commit()
        else:
            funnel_object = request.get_json()
            funnel = Funnels.query.filter(Funnels.funnel_name== funnel_object['funnelname']).delete()
            db.session.commit()
            notif = Notifs.query.filter(Notifs.funnel_name== funnel_object['funnelname']).delete()
            db.session.commit()
        return jsonify("Success"), 200








