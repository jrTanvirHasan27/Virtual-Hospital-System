from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///VirtualHospital.db'
app.config['SECRET_KEY'] = '94a19cf258601ce61162a6f2'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'welcome_page'
login_manager.login_message_category = 'info'
from VirtualHospital import routes

