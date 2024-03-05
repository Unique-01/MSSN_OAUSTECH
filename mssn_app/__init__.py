from flask import Flask
from decouple import config
import os
from flask_mail import Mail
from flask_ckeditor import CKEditor

ckeditor = CKEditor()


def create_app():
    app = Flask(__name__,instance_relative_config=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mssn.db'
    app.config['SECRET_KEY'] = config('SECRET_KEY')
    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] =config('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = config('MAIL_PASSWORD')
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    # app.config['CKEDITOR_PKG_TYPE'] = 'basic'

    from .models import db,migrate

    db.init_app(app)
    migrate.init_app(app, db)
    ckeditor.init_app(app)


    from . import auth
    from . import main
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    
    mail = Mail(app)

    
    return app

