from flask import Flask
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

def create_app(config):

    app = Flask(__name__)
    app.config.from_object(config)
    db = SQLAlchemy(app)
   
    login = LoginManager(app)
    login.login_view = 'login'

    bootstrap = Bootstrap(app)
    
    return app
