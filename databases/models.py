import json
from sqlalchemy.sql import func
from numpy import genfromtxt
import os
from appdb import  db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
here = os.path.dirname(os.path.abspath(__file__))





file_name = os.path.join(here, 'parentskus.csv')
file_name2 = os.path.join(here, 'quantities.csv')



class BaseModel(db.Model):
    __abstract__ = True

    def to_dict(self, show=None, _hide=[], _path=None):
        """Return a dictionary representation of this model."""

        show = show or []

        hidden = self._hidden_fields if hasattr(self, "_hidden_fields") else []
        default = self._default_fields if hasattr(self, "_default_fields") else []
        default.extend(['id', 'modified_at', 'created_at'])

        if not _path:
            _path = self.__tablename__.lower()

            def prepend_path(item):
                item = item.lower()
                if item.split(".", 1)[0] == _path:
                    return item
                if len(item) == 0:
                    return item
                if item[0] != ".":
                    item = ".%s" % item
                item = "%s%s" % (_path, item)
                return item

            _hide[:] = [prepend_path(x) for x in _hide]
            show[:] = [prepend_path(x) for x in show]

        columns = self.__table__.columns.keys()
        relationships = self.__mapper__.relationships.keys()
        properties = dir(self)

        ret_data = {}

        for key in columns:
            if key.startswith("_"):
                continue
            check = "%s.%s" % (_path, key)
            if check in _hide or key in hidden:
                continue
            if check in show or key in default:
                ret_data[key] = getattr(self, key)

        for key in relationships:
            if key.startswith("_"):
                continue
            check = "%s.%s" % (_path, key)
            if check in _hide or key in hidden:
                continue
            if check in show or key in default:
                _hide.append(check)
                is_list = self.__mapper__.relationships[key].uselist
                if is_list:
                    items = getattr(self, key)
                    if self.__mapper__.relationships[key].query_class is not None:
                        if hasattr(items, "all"):
                            items = items.all()
                    ret_data[key] = []
                    for item in items:
                        ret_data[key].append(
                            item.to_dict(
                                show=list(show),
                                _hide=list(_hide),
                                _path=("%s.%s" % (_path, key.lower())),
                            )
                        )
                else:
                    if (
                        self.__mapper__.relationships[key].query_class is not None
                        or self.__mapper__.relationships[key].instrument_class
                        is not None
                    ):
                        item = getattr(self, key)
                        if item is not None:
                            ret_data[key] = item.to_dict(
                                show=list(show),
                                _hide=list(_hide),
                                _path=("%s.%s" % (_path, key.lower())),
                            )
                        else:
                            ret_data[key] = None
                    else:
                        ret_data[key] = getattr(self, key)

        for key in list(set(properties) - set(columns) - set(relationships)):
            if key.startswith("_"):
                continue
            if not hasattr(self.__class__, key):
                continue
            attr = getattr(self.__class__, key)
            if not (isinstance(attr, property) or isinstance(attr, QueryableAttribute)):
                continue
            check = "%s.%s" % (_path, key)
            if check in _hide or key in hidden:
                continue
            if check in show or key in default:
                val = getattr(self, key)
                if hasattr(val, "to_dict"):
                    ret_data[key] = val.to_dict(
                        show=list(show),
                        _hide=list(_hide), _path=("%s.%s" % (_path, key.lower()))
                    )
                else:
                    try:
                        ret_data[key] = json.loads(json.dumps(val))
                    except:
                        pass

        return ret_data


class Users(UserMixin, BaseModel):
    """Model for user accounts."""

    __tablename__ = 'flasklogin'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer,
                   primary_key=True)
    name = db.Column(db.String,
                     nullable=False,
                     unique=False)
    email = db.Column(db.String(40),
                      unique=True,
                      nullable=False)
    password = db.Column(db.String(200),
                         primary_key=False,
                         unique=False,
                         nullable=False)
    website = db.Column(db.String(60),
                        index=False,
                        unique=False,
                        nullable=True)
    created_on = db.Column(db.DateTime,
                           index=False,
                           unique=False,
                           nullable=True)
    last_login = db.Column(db.DateTime,
                           index=False,
                           unique=False,
                           nullable=True)

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password, method='sha256')

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Sku(UserMixin, BaseModel):
    """Model for the stations table"""
    __tablename__ = 'skus'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key = True)
    sku = db.Column(db.Unicode)
    order_date = db.Column(db.Date, server_default=func.now())
    order_number = db.Column(db.Unicode)

    @property
    def serialize(self):
       """Return object data in easily serializable format"""
       return {
           'id': self.id,
           'sku': self.sku,
           # This is an example how to deal with Many2Many relations
           'order_date': self.order_date,
           'order_number' : self.order_number

       }

       def __init__(self, id, sku, order_date, order_number):
           self.id = id
           self.sku = sku
           self.order_date = order_date
           self.order_number = order_number



class Sales(UserMixin,BaseModel):
    """Model for the stations table"""
    __tablename__ = 'funnel_metrics'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key = True)
    order_id = db.Column(db.Integer)
    funnel_id = db.Column(db.Unicode)
    email = db.Column(db.Unicode)
    product_id = db.Column(db.Unicode)
    price = db.Column(db.Numeric(5,2))
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    product_name = db.Column(db.Unicode)
    @property
    def serialize(self):
       """Return object data in easily serializable format"""
       return {
           'id': self.id,
           'order_id': self.order_id,
           'funnel_id': self.funnel_sku,
           # This is an example how to deal with Many2Many relations
           'email': self.email,
           'product_id' : self.product_id,
           'price' : self.price,
           'time_created' : self.time_created,
           'product_name' : self.product_name

       }

       def __init__(self, order_id,funnel_id, email, product_id, price, time_created, product_name):
           self.id = id
           self.order_id = order_id
           self.funnel_id = funnel_id
           self.email = self.email
           self.product_id = product_id
           self.price = price
           self.time_created = time_created
           self.product_name = product_name


class Funnels(UserMixin, BaseModel):
    """Model for the stations table"""
    __tablename__ = 'funnel_identities'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key = True)
    funnel_name = db.Column(db.Unicode)
    funnel_id = db.Column(db.Unicode)
    view_id = db.Column(db.Unicode)
    stats_link = db.Column(db.Unicode)
    optin = db.Column(db.Unicode)

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
            "optin" : self.optin

       }

       def __init__(self, funnel_name,funnel_id, stats_link, view_id, optin):
           self.funnel_name = funnel_name
           self.funnel_id = funnel_id
           self.view_id = self.view_id
           self.stats_link = self.stats_link
           self.optin = self.optin

class Emails(UserMixin, BaseModel):
    """Model for the stations table"""
    __tablename__ = 'email_funnels'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key = True)
    funnel_id = db.Column(db.Unicode)
    email = db.Column(db.Unicode)
    updated = db.Column(db.Boolean)
    answer = db.Column(db.Unicode)
    question = db.Column(db.Unicode)
    time_created = db.Column(db.DateTime(timezone=False), server_default=func.now())
    @property
    def serialize(self):
       """Return object data in easily serializable format"""
       return {
           'id': self.id,
           'updated': self.updated,
           'funnel_id': self.funnel_sku,
           # This is an example how to deal with Many2Many relations
           'email': self.email,
           'time_created' : self.time_created,
           'question' : self.question,
           'answer' : self.answer


       }

       def __init__(self, id,funnel_id, email, time_created, question, answer, updated):
           self.id = id
           self.funnel_id = funnel_id
           self.email = self.email
           self.time_created = time_created
           self.question = question
           self.answer = answer
           self.updated = updated

class Parentsku(UserMixin, BaseModel):
    """Model for the stations table"""
    __tablename__ = 'parentskus'
    __table_args__ = {'extend_existing': True}
    p_id = db.Column(db.Integer, primary_key = True)
    parent_sku = db.Column(db.Unicode)
    featured = db.Column(db.Boolean, default=False)
    encorestock = db.Column(db.Integer, default=0)
    inboundstock = db.Column(db.Integer, default=0)
    day1 = db.Column(db.Integer, default=0)
    day3 = db.Column(db.Integer, default=0)
    day7 = db.Column(db.Integer, default=0)
    day14 = db.Column(db.Integer, default=0)
    day28 = db.Column(db.Integer, default=0)
    #childsku = db.relationship('Quantities.child_sku', backref='owner')


    def __init__(self, parent_sku, featured, encorestock, inboundstock,day1, day3, day7, day14, day28):
        self.parent_sku = parent_sku
        self.featured = featured
        self.encorestock = encorestock
        self.inboundstock = inboundstock
        self.day1 = day1
        self.day3 = day3
        self.day7 = day7
        self.day14 = day14
        self.day28 = day28
    @property
    def serialize(self):
       """Return object data in easily serializable format"""
       return {
            'p_id': self.p_id,
            'parent_sku': self.parent_sku,
            'featured': self.featured,
            'encorestock' : self.encorestock,
            'inboundstock' : self.inboundstock,
            'day1' : self.day1,
            'day3': self.day3,
            'day7': self.day7,
            'day14': self.day14,
            'day28': self.day28
           # This is an example how to deal with Many2Many relations
       }

class Quantities(UserMixin, BaseModel):

    __tablename__='skuquantities'
    __table_args__ = {'extend_existing': True}


    c_id = db.Column(db.Integer, primary_key = True)
    child_sku = db.Column(db.Unicode)
    quantity = db.Column(db.Integer)
    parent_sku = db.Column(db.Integer, db.ForeignKey('parentskus.p_id'))




    @property
    def serialize(self):
       """Return object data in easily serializable format"""
       return {
           'c_id'         : self.c_id,
           'child_sku': self.child_sku,
           # This is an example how to deal with Many2Many relations
           'quantity'  : self.quantity,
           'parent_sku' : self.parent_sku
       }
    @property
    def serialize_many2many(self):
       """
       Return object's relations in easily serializable format.
       NB! Calls many2many's serialize property.
       """
       return [ item.serialize for item in self.many2many]



class Notifs(UserMixin, BaseModel):

    __tablename__='notif_settings'
    __table_args__ = {'extend_existing': True}


    id = db.Column(db.Integer, primary_key = True)
    funnel_name = db.Column(db.Unicode)
    sms = db.Column(db.Boolean)
    email = db.Column(db.Boolean)




    @property
    def serialize(self):
       """Return object data in easily serializable format"""
       return {
           "id" : self.id,
           "funnel_name" : self.funnel_name,
           "sms" : self.sms,
           "email" : self.email
       }
    @property
    def serialize_many2many(self):
       """
       Return object's relations in easily serializable format.
       NB! Calls many2many's serialize property.
       """
       return [ item.serialize for item in self.many2many]



class Contacts(BaseModel):

    __tablename__='notif_contacts'
    __table_args__ = {'extend_existing': True}


    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.Unicode)
    phone = db.Column(db.Unicode)
    email = db.Column(db.Unicode)

    def __init__(self, id, name, phone, email):
        self.id = id
        self.name = name
        self.phone = phone
        self.email = email


    @property
    def serialize(self):
       """Return object data in easily serializable format"""
       return {
           "id" : self.id,
           "name" : self.name,
           "phone" : self.phone,
           "email" : self.email
       }
    @property
    def serialize_many2many(self):
       """
       Return object's relations in easily serializable format.
       NB! Calls many2many's serialize property.
       """
       return [ item.serialize for item in self.many2many]

class SuppressedEmails(BaseModel):

    __tablename__='suppressed_emails'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.Unicode)
    date_inserted = db.Column(db.Unicode)


    def __init__(self, email, date_inserted):
        self.id
        self.email = email
        self.date_inserted = date_inserted

    @property
    def serialize(self):
       """Return object data in easily serializable format"""
       return {
           "id" : self.id,
           "email" : self.email,
           "date_inserted" : self.date_inserted
       }
    @property
    def serialize_many2many(self):
       """
       Return object's relations in easily serializable format.
       NB! Calls many2many's serialize property.
       """
       return [ item.serialize for item in self.many2many]

class shipstationAddresses(BaseModel):

    __tablename__='ss_addresses'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key = True)
    customer_email = db.Column(db.Unicode)
    name = db.Column(db.Unicode)
    order_number = db.Column(db.Unicode)


    def __init__(self, name, customer_email, order_number):
        self.id
        self.customer_email = customer_email
        self.name = name
        self.order_number = order_number

    @property
    def serialize(self):
       """Return object data in easily serializable format"""
       return {
           "id" : self.id,
           "customer_email" : self.customer_email,
           "order_number" : self.order_number,
           "name" : self.name
       }
    @property
    def serialize_many2many(self):
       """
       Return object's relations in easily serializable format.
       NB! Calls many2many's serialize property.
       """
       return [ item.serialize for item in self.many2many]
class Methods:

    def start_parentsku_import(self):
        data = genfromtxt(file_name, delimiter=',',dtype='U50')
        for x in data:
            new_sku = Parentsku(parent_sku=x)
            db.session.add(new_sku)
            db.session.commit()
        return 'success'

    def start_childsku_import(self):
        data = genfromtxt(file_name2, delimiter=',',dtype=['U50','<i8'])

        for x in range(len(data)):
            new_sku = Quantities(child_sku=data[x][0], quantity=int(data[x][1]))
            db.session.add(new_sku)
            db.session.commit()

        return data[0][0]

    def assignparent(self):
        parent = db.session.query(Parentsku).all();
        child = db.session.query(Quantities).all();
        for p_item in parent:
            for c_item in child:
                if p_item.parent_sku not in c_item.child_sku:
                    continue;
                else:
                    c_item.parent_sku = p_item.p_id
                    db.session.commit()





