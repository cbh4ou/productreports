import sys
sys.path.append('/home/jkwent/productreports')
from flask_app import test_items
from databases.models import Sku
from appdb import db

test_items()

db.session.query(Sku).all()

