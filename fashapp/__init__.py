import os
from dotenv import load_dotenv
from flask import Flask

from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail


from fashapp import config

from fashapp.models import db
load_dotenv()

csrf =CSRFProtect()
mail =Mail()

def create_app():
    from fashapp import models

    app = Flask(__name__,instance_relative_config=True)

    app.config.from_pyfile("config.py")
    app.config.from_object(config.BaseConfig)

    db.init_app(app)
    migrate=Migrate(app,db)
    csrf.init_app(app)
    mail.init_app(app)

    return app
app =create_app()

from fashapp import user_route,admin_route