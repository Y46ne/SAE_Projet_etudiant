from flask import Flask, render_template  
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap5 import Bootstrap
from flask_login import LoginManager

app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')
app.config.from_object('config')

db = SQLAlchemy()
db.init_app(app)

Bootstrap(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
app.config['SQLALCHEMY_ECHO'] = True