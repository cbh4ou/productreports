    # A very simple Flask Hello World app for you to get started with...

from flask import request, render_template, redirect, url_for, jsonify
from databases.models import Sku, Methods, Parentsku, Quantities, Funnels
import json
import requests
from . import app, db
from datetime import date, timedelta, datetime
import pandas as pd
import demjson
import os
from werkzeug.utils import secure_filename
import time
from flask_login import login_required
import csv
import pandas
import csv
ALLOWED_EXTENSIONS = set(['csv', 'xlsx'])

inbound_upload_time = None
stock_upload_time = None

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

here = os.path.dirname(os.path.abspath(__file__))

order_list_import = os.path.join(here, 'order-list.csv')
encore_stock = os.path.join(here, 'rslt.xlsx')
records = os.path.join(here, 'recordtimes.txt')

@app.route('/importnowplz', methods=['POST'])
def import_now():

    # check if the post request has the file part
	if 'file' not in request.files:
		resp = jsonify({'message' : 'No file part in the request'})
		resp.status_code = 400
		return resp
	file = request.files['file']

	if file.filename == '':
		resp = jsonify({'message' : 'No file selected for uploading'})
		resp.status_code = 400
		return resp

	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		encore_stock = os.path.join(here,filename)
		if os.path.exists(encore_stock):
		    os.remove(encore_stock)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		time.sleep(1)
		with open(encore_stock, 'r') as file:
		    reader = csv.reader(file)
		    for row in reader:
		        add_funnel = Funnels(funnel_name=row[1], funnel_id = row[2], stats_link = row[4], view_id = row[3], optin = row[5])
		        db.session.add(add_funnel)
		        db.session.commit()

		resp = jsonify({'message' : 'File successfully uploaded'})
		resp.status_code = 201
		with open(records, "r") as file:
		    lines = file.readlines()
		with open(records, 'w') as file:
		    file.writelines(lines)
		return resp

	else:
		resp = jsonify({'message' : 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'})
		resp.status_code = 400
		return resp

	file_name = 'fisheet.csv'

	with open(file_name, 'r') as file:
	    reader = csv.reader(file)
	    for row in reader:
	        add_funnel = Funnels(funnel_name=row[0], funnel_id = row[1], view_id = row[2])
	        db.session.add(add_funnel)
	        db.session.commit()

	        return 'thanks'

@app.route('/')
@login_required
def test_main():
    today_arr = []
    thirdday_arr = []
    sevenday_arr = []
    fourteenday_arr = []
    twentyeightday_arr = []
    num = []
    parent_final = []
    word = (db.session.query(Parentsku)
            .all())
    for item in word:
        today_arr.append(item.day1)
        thirdday_arr.append(item.day3)
        sevenday_arr.append(item.day7)
        fourteenday_arr.append(item.day14)
        twentyeightday_arr.append(item.day28)
        parent_final.append(item.parent_sku)
        #stock_left.append()
    stockarr = query_stock(False, 'encore')
    inbound_arr = query_stock(False, 'inbound')

    num.append(today_arr)
    num.append(thirdday_arr)
    num.append(sevenday_arr)
    num.append(fourteenday_arr)
    num.append(twentyeightday_arr)
    num.append(stockarr)
    num.append(inbound_arr)


    days = ['Today','3 days', '7 days', '14 days', '28 days', 'In Stock', 'Inbound']
    df = pd.DataFrame(num, index=days, columns=parent_final)
    df = df.T
    html = df.to_html()


    with open(records, "r") as file:
		    lines = file.readlines()

    return render_template("skudataTable.html", data=html, inbound = lines[1], stock = lines[0])

@app.route('/featured')
@login_required
def test_feature():

    num = []
    newarr5, parent_final = create_f_table(1)
    newarr4, parent_final = create_f_table(3)
    newarr3, parent_final = create_f_table(7)
    newarr2, parent_final = create_f_table(14)
    newarr, parent_final = create_f_table(28)
    stockarr = query_stock(True, 'encore')
    inbound_arr = query_stock(True, 'inbound')

    num.append(newarr5)
    num.append(newarr4)
    num.append(newarr3)
    num.append(newarr2)
    num.append(newarr)
    num.append(stockarr)
    num.append(inbound_arr)
    days = ['Today','3 days', '7 days', '14 days', '28 days', 'In Stock', 'Inbound']

    df = pd.DataFrame(num, index=days, columns=parent_final)
    df = df.T
    html = df.to_html()
    with open(records, "r") as file:
		    lines = file.readlines()
    return render_template("skudataTable.html", data=html,  inbound = lines[1],stock = lines[0]  )


@app.route('/funnelstats')
@login_required
def metric_table():

    return render_template("metric_table.html")


def query_stock(t, inven_type):
    if inven_type == 'encore':
        featured_skus = None
        parent_skus_arr = []
        if t:
            featured_skus = db.session.query(Parentsku).filter(Parentsku.featured==True).all()
        else:
            featured_skus = db.session.query(Parentsku).all()

        for i in featured_skus:
            if i.encorestock != None:
                parent_skus_arr.append(i.encorestock)
            else:
                parent_skus_arr.append(0)

        return parent_skus_arr
    elif inven_type == 'inbound':
        featured_skus = None
        parent_skus_arr = []
        if t:
            featured_skus = db.session.query(Parentsku).filter(Parentsku.featured==True).all()
        else:
            featured_skus = db.session.query(Parentsku).all()

        for i in featured_skus:
            if i.inboundstock != None:
                parent_skus_arr.append(i.inboundstock)
            else:
                parent_skus_arr.append(0)

        return parent_skus_arr


@app.route('/emailfunnelstats')
@login_required
def email_funnel():
    return render_template("funnelsTable.html")


def create_f_table(days):
    # Set order dates
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
            .filter(Parentsku.featured==True)
            .all())

    else:
        # Query Table Join
        word = (db.session.query(Sku, Parentsku, Quantities)
            .join(Quantities, Quantities.child_sku == Sku.sku)
            .join(Parentsku)
            .filter(Sku.order_date == start_date)
            .filter(Parentsku.featured==True)
            .all())


    start_date = start_date.strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")

    # Set of arrays to pass back to Dataframe Table
    quantity = []
    parent_skus_arr = []
    featured_skus = db.session.query(Parentsku).filter(Parentsku.featured==True).all()
    for i in featured_skus:
        parent_skus_arr.append(i.parent_sku)
    parent_final = list(dict.fromkeys(parent_skus_arr))

    for index_range in range(len(parent_final)):
        quantity.append(0)

    for psku in parent_final:
        for i in word:
            if i.Parentsku.parent_sku == psku:
                quantity[parent_final.index(psku)] += i.Quantities.quantity

    return quantity, parent_final


def create_t_table(days):
    # Set order dates
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

    else:
        # Query Table Join
        word = (db.session.query(Sku, Parentsku, Quantities)
            .join(Quantities, Quantities.child_sku == Sku.sku)
            .join(Parentsku)
            .filter(Sku.order_date == start_date)
            .all())


    start_date = start_date.strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")

    # Set of arrays to pass back to Dataframe Table
    quantity = []
    parent_skus_arr = []
    featured_skus = db.session.query(Parentsku).all()
    for i in featured_skus:
        parent_skus_arr.append(i.parent_sku)
    parent_final = list(dict.fromkeys(parent_skus_arr))
    for index_range in range(len(parent_final)):
        quantity.append(0)

    for psku in parent_final:
        for i in word:
            if i.Parentsku.parent_sku == psku:
                quantity[parent_final.index(psku)] += i.Quantities.quantity

    return quantity, parent_final

def get_quantity(s):
    tempquant = db.session.query(Quantities).filter_by(child_sku=s).first()
    return tempquant.quantity

@app.route('/itemorder', methods=['POST'])
def receive_item():
    foo = request.get_data()
    python_obj = json.loads(foo)
    sku_quant = python_obj['quantity']
    for quant in range(sku_quant):
        new_sku = Sku(sku=python_obj['sku'], order_number=python_obj['order_number'],
        order_date=python_obj['order_date'])
        db.session.add(new_sku)
        db.session.commit()
    return jsonify({'status': 200}),200

@app.route('/cancelorders', methods=['GET'])
def cancel_items():
    orders_today = datetime.now().strftime("%Y-%m-%d")
    url = "https://ssapi6.shipstation.com/orders"
    querystring = {"orderDate":orders_today, "orderStatus":"cancelled", "sortDir":"DESC"}

    headers = {
            'Content-Type': "application/json",
            'Authorization': "Basic NGQyMmJhYWI0NjlmNDlhNzk0ZjhmMzAwMmI3NTZjMGE6ODc5NDkyYjlhNTBhNGZmYTkyM2E5ZjI2NzY0OTYwZmE=",
            'Accept': "*/*",
            'Cache-Control': "no-cache",
            'Host': "ssapi6.shipstation.com",
            'Accept-Encoding': "gzip, deflate",
            'Connection': "keep-alive",
            'cache-control': "no-cache"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    data = response.json()
    sku_data = data['orders']
    for x in range(len(sku_data)):
        db.session.query(Sku).filter(Sku.order_number == sku_data[x]['orderNumber']).delete()
        db.session.commit()
    return jsonify("Success"), 200


@app.route('/importcsv', methods=['GET'])
def importcsv():
    loaddata = Methods()
    return loaddata.start_parentsku_import()




@app.route('/editsku', methods=['GET', 'POST'])
@login_required
def editsku():
    error = None
    if request.method == 'POST':
        if request.form['input1'] != '':
            error = 'Invalid Credentials. Please try again.'
            return redirect(url_for('editsku'))
        else:
            return redirect(url_for(''))
    return render_template('editsku.html', error=error)


# Returns search query to front-end
@app.route('/editsku/<parentsku>/<newparent>/<status>', methods=['GET','POST'])
@login_required
def editskuroute(parentsku, newparent, status):
    if request.method == 'POST':
        data = request.get_data()
        child_skus = demjson.decode(data)
        if parentsku == 'none' and newparent != 'none':
            new_sku = Parentsku(parent_sku=newparent, featured = True , encorestock = 0, inboundstock = 0, day1=0, day3=0, day7=0, day14=0, day28=0)
            db.session.add(new_sku)
            db.session.commit()

            addchildskus(child_skus, newparent)
            setfeature(status,newparent)
            return jsonify('Success: Child Skus edited'), 200

        elif parentsku != 'none' and newparent != 'none' :
            changeparent = db.session.query(Parentsku).filter_by(parent_sku=parentsku).first()
            changeparent.parent_sku = newparent
            db.session.commit()
            time.sleep(1)
            addchildskus(child_skus, newparent)
            setfeature(status,newparent)
            return jsonify('Success: Child Skus edited'), 200

        elif parentsku != 'none' and newparent == 'none':

            addchildskus(child_skus, parentsku)
            setfeature(status,parentsku)
            return jsonify('Success: Child Skus edited'), 200

    # If request is GET
    else:
        parent_sku = db.session.query(Parentsku).filter(Parentsku.parent_sku==parentsku).first()
        if parent_sku.featured: return 'true',200
        else: return 'false',200

def addchildskus(child_skus, parentsku):
    addparent = db.session.query(Parentsku).filter_by(parent_sku=parentsku).first()
    db.session.query(Quantities).filter_by(parent_sku=addparent.p_id).delete()
    db.session.commit()
    for key in child_skus:
        if key == '':
            continue
        else:
            newchild = Quantities(child_sku=key, quantity=child_skus[key], parent_sku=addparent.p_id)
            db.session.add(newchild)
            db.session.commit()

def setfeature(status, parentsku):
    parent_sku = db.session.query(Parentsku).filter(Parentsku.parent_sku==parentsku).first()
    if status == 'true':
        parent_sku.featured = True
        db.session.commit()
    else:
        parent_sku.featured = False
        db.session.commit()

@app.route('/delete/<parentsku>', methods=['GET','POST'])
@login_required
def delete_sku(parentsku):
    if request.method == 'POST':
        db.session.query(Parentsku).filter_by(parent_sku=parentsku).delete()
        db.session.commit()
        return jsonify('Sku Deleted'), 200



# Returns search query to front-end
@app.route('/editsku/<parentsku>', methods=['GET','POST'])
@login_required
def editskuroutetest(parentsku):
    newparent = None
    if request.method == 'POST':
        if newparent == 'none':
            data = request.get_data()
            child_skus = demjson.decode(data)
            for key in child_skus:
                child = db.session.query(Quantities).filter_by(child_sku=key).first()
                child.child_sku = key
                child.quantity = child_skus[key]
                db.session.commit()
                return jsonify('success'), 200
        else:
            data = request.get_data()
            child_skus = demjson.decode(data)
            return jsonify(child_skus['TACPEN-001']), 200
    else:
        p_sku = db.session.query(Parentsku).filter_by(parent_sku=parentsku).first()
        if p_sku is None:
            return redirect('/')
        child_skus = db.session.query(Quantities, Parentsku).join(Parentsku).filter(Quantities.parent_sku==p_sku.p_id)
        skus =[i.Quantities.child_sku for i in child_skus]
        quantity =[i.Quantities.quantity for i in child_skus]
        return jsonify(dict(zip(skus, quantity))), 200




@app.errorhandler(404)
def page_not_found(e):
    return jsonify("Page not found"), 404



@app.route('/order-list-import', methods=['GET','POST'])
def order_list():
    df = pd.read_csv(order_list_import, header=None, delimiter=',')

    for x in range(len(df)):
        for repeat in range(df[2][x]):
            new_sku = Sku(sku=df[0][x], order_date=df[1][x])
            db.session.add(new_sku)
            db.session.commit()



@app.route('/file-upload', methods=['POST'])
def upload_file():
	# check if the post request has the file part
	if 'file' not in request.files:
		resp = jsonify({'message' : 'No file part in the request'})
		resp.status_code = 400
		return resp
	file = request.files['file']

	if file.filename == '':
		resp = jsonify({'message' : 'No file selected for uploading'})
		resp.status_code = 400
		return resp

	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		encore_stock = os.path.join(here,filename)
		if os.path.exists(encore_stock):
		    os.remove(encore_stock)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		time.sleep(5)
		df = pd.read_excel(encore_stock, header=None, delimiter=',')
		df.drop(df.tail(1).index,inplace=True)
		df.drop(df.head(2).index,inplace=True)
		df = df.reset_index(drop=True)
		for x in range(len(df)):
		    if df[4][x] == "BUNDLE":
		        continue
		    else:
		        result = db.session.query(Parentsku).join(Quantities, Quantities.parent_sku == Parentsku.p_id).filter(Quantities.child_sku==df[1][x]).first()
		        if result is None:
		            continue
		        elif result.encorestock is None:
		            result.encorestock = 0
		            db.session.commit()
		        else:
		            result.encorestock = df[10][x]
		            db.session.commit()

		resp = jsonify({'message' : 'File successfully uploaded'})
		resp.status_code = 201
		with open(records, "r") as file:
		    lines = file.readlines()
		lines[0] = datetime.now().strftime("%Y-%m-%d %H:%M:%S") +"\n"
		with open(records, 'w') as file:
		    file.writelines(lines)
		return resp

	else:
		resp = jsonify({'message' : 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'})
		resp.status_code = 400
		return resp


@app.route('/inbound-upload', methods=['POST'])
def inbound_upload():

    if 'file' not in request.files:
	    resp = jsonify({'message' : 'No file part in the request'})
	    resp.status_code = 400
	    return resp

	# check if the post request has the file part
    file = request.files['file']

    if file.filename == '':
	    resp = jsonify({'message' : 'No file selected for uploading'})
	    resp.status_code = 400
	    return resp

    elif file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        encore_stock = os.path.join(here,filename)
        if os.path.exists(encore_stock):
            os.remove(encore_stock)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        time.sleep(5)
        df = pd.read_excel(encore_stock, 'Inbound',header=None, delimiter=',')
        df.drop(df.head(1).index,inplace=True)
        df = df.reset_index(drop=True)
        for x in range(len(df)):
            result = db.session.query(Parentsku).join(Quantities, Quantities.parent_sku == Parentsku.p_id).filter(Quantities.child_sku==df[0][x]).first()
            if result is None:
                continue
            elif result.inboundstock is None:
                result.inboundstock = 0
                db.session.commit()
            elif pd.isnull(df[1][x]):
                result.inboundstock = 0
                db.session.commit()
            else:
                result.inboundstock = df[1][x]
                db.session.commit()
        resp = jsonify({'message' : 'File successfully uploaded'})
        resp.status_code = 201
        with open(records, "r") as file:
            lines = file.readlines()
            lines[1] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(records, 'w') as file:
            file.writelines(lines)
        return resp

    else:
        resp = jsonify({'message' : 'Allowed file types is xlsx'})
        resp.status_code = 400
        return resp




@app.route('/ss-upload', methods=['POST'])
def ss_upload():
	# check if the post request has the file part
	if 'file' not in request.files:
		resp = jsonify({'message' : 'No file part in the request'})
		resp.status_code = 400
		return resp
	file = request.files['file']

	if file.filename == '':
		resp = jsonify({'message' : 'No file selected for uploading'})
		resp.status_code = 400
		return resp

	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		encore_stock = os.path.join(here,filename)
		if os.path.exists(encore_stock):
		    os.remove(encore_stock)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		time.sleep(1)
		df = pd.read_excel(encore_stock, 'Sheet1',header=None, delimiter=',')
		for x in range(len(df)):
		      for add in range(0 , df[2][x]):
		          additem = Sku(sku=df[0][x], order_date=df[1][x])
		          db.session.add(additem)
		          db.session.commit()

		resp = jsonify({'message' : 'File successfully uploaded'})
		resp.status_code = 201
		with open(records, "r") as file:
		    lines = file.readlines()
		with open(records, 'w') as file:
		    file.writelines(lines)
		return resp

	else:
		resp = jsonify({'message' : 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'})
		resp.status_code = 400
		return resp


