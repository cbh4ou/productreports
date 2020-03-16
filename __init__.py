import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

POSTGRES = {
    'user': 'jkwuser',
    'pw': 'a-nice-random-password',
    'db': 'skudb',
    'host': '10.0.0.46',
    'port': '11366',
}
mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 587,
    "MAIL_USE_TLS": True,
    "MAIL_USE_SSL": False,
    "MAIL_USERNAME": "cbh4ou@gmail.com",
    "MAIL_PASSWORD": "Soniamyheart72!"
}

app = Flask(__name__,template_folder='assets/templates',static_url_path='', static_folder='assets')
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app.config.update(mail_settings)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config.from_object('config.Config')
app.config['DEBUG'] = False
app.config['UPLOAD_FOLDER'] = os.path.dirname(os.path.abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
db = SQLAlchemy(app)
mail = Mail(app)




login_manager = LoginManager()
login_manager.init_app(app)

from . import auth, routes, auth_routes, funnel_stats

app.register_blueprint(routes.main_bp)
app.register_blueprint(auth.auth_bp)
app.register_blueprint(auth_routes.oauth_bp)
app.register_blueprint(funnel_stats.metrics_bp)
from . import flask_app
