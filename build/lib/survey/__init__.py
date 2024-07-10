from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

app = Flask(__name__)

# Estensioni senza configurazioni iniziali
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
bootstrap = Bootstrap()

# Funzione per impostare la configurazione
def set_config(config):
    app.config.from_object(config)
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    login.login_view = 'login'
    bootstrap.init_app(app)

# Import delle routes e dei modelli
from . import routes
from . import models

