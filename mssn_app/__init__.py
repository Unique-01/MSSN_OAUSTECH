from flask import Flask
from decouple import config
import os

def create_app():
    app = Flask(__name__,instance_relative_config=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mssn.db'
    app.config['SECRET_KEY'] = config('SECRET_KEY')

    from .models import db,migrate

    db.init_app(app)
    migrate.init_app(app, db)

    from . import auth
    from . import main
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    

    
    return app