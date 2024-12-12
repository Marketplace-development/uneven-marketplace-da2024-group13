import os
import sys
if sys.platform == "win32":
    
    os.add_dll_directory(r"C:\Program Files\PostgreSQL\17\bin")

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    db.init_app(app)
    migrate.init_app(app, db)
    #with app.app_context():
        #db.drop_all()
        #db.create_all()
    
    from .routes import register_routes
    register_routes(app)

    return app
