from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'MyKeyIsSecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://c1841568:~Quiapo09sql@csmysql.cs.cf.ac.uk:3306/c1841568'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

from myShop import routes
