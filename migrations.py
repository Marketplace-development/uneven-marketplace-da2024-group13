from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from . import db

app = Flask(__name__)
app.config.from_object("config.Config")

#db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Example model
# class User(db.Model):
# id = db.Column(db.Integer, primary_key=True)
# name = db.Column(db.String(50), nullable=False)


# if __name__ == "__main__":
# app.run(debug=True)

