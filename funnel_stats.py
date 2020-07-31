"""Routes for logged-in application."""
from flask import Blueprint, render_template, redirect, jsonify, request
from appdb import db
from datetime import date, timedelta, datetime, timezone
from databases.models import  Sales, Funnels, Emails
import requests
from decimal import Decimal
from collections import Counter

# Blueprint Configuration
metrics_bp = Blueprint('metrics_bp', __name__,
                    template_folder='assets/templates',
                    static_folder='assets')





class Funnel_stats:
	def __init__(self, funnelname, pageviews, sales, revenue, aov,epc,cr, stats_link):
		self.funnelname = funnelname
		self.pageviews = str(pageviews)
		self.sales = sales
		self.revenue = str(revenue)
		self.aov = str(aov)
		self.epc = str(epc)
		self.cr = str(cr)
		self.stats_link = str(stats_link)



class Email_funnel:
	def __init__(self, funnelname, pageviews, optins, created, updated, optin_rate, stats_link):
		self.funnelname = funnelname
		self.pageviews = str(pageviews)
		self.optins = optins
		self.created = str(created)
		self.updated = str(updated)
		self.optin_rate = optin_rate
		self.stats_link = str(stats_link)


def request_views(view_id, start_date, end_date):

    url = "https://inventory.jkwenterprises.com/test/%s/%s/%s" % (view_id,start_date, end_date)

    payload = 'client_id=331921780182-n2sfr26lvjphn427mth2jcfm7i5b7io1.apps.googleusercontent.com&client_secret=0GFhgD5YUivcvclSEYDfUPNt&refresh_token=1//04Tl-CuRdYeA6CgYIARAAGAQSNwF-L9IrKONUqcwHhQ64yedf_aw-oulcWkNZfuwrPpLYwj67O3IaB2trOmnEYM_76fYuKe7au_Q&grant_type=refresh_token'
    headers = {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
    response = requests.request("GET", url, headers=headers, data = payload)

    return response





@metrics_bp.route('/metrics/emails/<start_date>/<end_date>', methods=['GET'])
def email_metrics(start_date, end_date):
    if start_date == end_date:
      end_date = datetime.strftime(datetime.now(timezone.utc) + timedelta(1), '%Y-%m-%d')
    start = start_date
    end = end_date
    email_funnels = db.session.query(Funnels).all()

    funnels = {'data' : []}
    for x in email_funnels:
        stats_link = None
        data = None
        page_views = 0
        optins = 0
        created = 0
        updated = 0
        email_count = []
        optin_rate = 0

        funnel_query = (db.session.query(Funnels, Emails)
            .join(Emails, Emails.funnel_id == Funnels.funnel_id)
            .filter(Emails.time_created >= start_date, Emails.time_created <= end_date, Emails.funnel_id == x.funnel_id)
            .first())

        if funnel_query == None:
            continue

        optins = db.session.query(Emails).filter(Emails.time_created >= start_date, Emails.time_created <= end_date, Emails.funnel_id == x.funnel_id).count()
        db.session.close()
        if optins != 0:
             created = (len(email_count)/optins) * 100
             updated = ((optins - len(email_count))/optins) * 100

        response = request_views(funnel_query.Funnels.view_id ,start, end)
        data = response.json()
        page_views = int(data['reports'][0]['data']['totals'][0]['values'][0])
        stats_link = "https://patpubs-app.clickfunnels.com/funnels/" +  x.funnel_id +  "/stats"

        if page_views != 0:
            optin_rate = ((optins/page_views) * 100)
            stats = Email_funnel(x.funnel_name, page_views,  optins, "%.2f" %  created, "%.2f" %  updated, "%.2f" % optin_rate, stats_link)
            funnels['data'].append(stats.__dict__)


    return jsonify(funnels)


@metrics_bp.route('/metrics/sales/<start_date>/<end_date>', methods=['GET'])
def get_metrics(start_date, end_date):
    start = start_date
    end = end_date


    funnels = {'data' : []}
    rev = db.session.query(Sales).filter().distinct(Sales.funnel_id)
    db.session.close()
    for x in rev:
        f_id = x.funnel_id
        # Query and Make request to GA API
        view = db.session.query(Funnels).filter(Funnels.funnel_id == f_id).first()
        db.session.close()
        if view is None:
            continue
        else:
            response = request_views(view.view_id ,start, end)
        data = response.json()

        page_views = int(data['reports'][0]['data']['totals'][0]['values'][0])


        sales, revenue = calc_revenue(f_id, start, end)

        if sales == 0:
            aov = 0
        else:
            aov = revenue/sales

        if page_views == 0:
            epc = 0
            cr = 0
        else:
            epc = Decimal(revenue)/Decimal(page_views)
            cr = (Decimal(sales)/Decimal(page_views)) * 100
        stats_link = "https://patpubs-app.clickfunnels.com/funnels/" +  view.funnel_id +  "/stats"
        stats = Funnel_stats(view.funnel_name, page_views, sales, revenue,"%.2f" % aov,"%.2f" % epc , "%.2f" % cr, stats_link)
        funnels['data'].append(stats.__dict__)
    return jsonify(funnels)


def calc_revenue(funnel_id, start_date, end = datetime.now(timezone.utc) ):
    revenue = 0
    orders = []
    if start_date == end:
        end = datetime.strftime(datetime.now(timezone.utc) + timedelta(1), '%Y-%m-%d')
    rev = db.session.query(Sales).filter(Sales.time_created >= start_date, Sales.time_created <= end,  Sales.funnel_id == funnel_id).all()
    for i in rev:
        orders.append(i.order_id)
        revenue += i.price
    return countDistinct(orders), revenue


def countDistinct(arr):

    # counter method gives dictionary of elements in list
    # with their corresponding frequency.
    # using keys() method of dictionary data structure
    # we can count distinct values in array
    return len(Counter(arr).keys())