from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

from datetime import datetime

from routes import routes

app = Flask(__name__)
app.config['SECRET_KEY'] = "justarandomsecretkeypassingby"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/database.db'
app.config['SQLALCHEMY_BINDS'] = {
    'data': 'sqlite:///db/data',
    'user': 'sqlite:///db/user'
}
db = SQLAlchemy(app)
Bootstrap(app)


class User(db.Model):
    __bind_key__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

    def __repr__(self):
        return '<User %r>' % self.id


class RealEstate(db.Model):
    __bind_key__ = 'data'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    rooms = db.Column(db.Integer, nullable=False)
    landlord = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(200), nullable=False)

    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Property %r>' % self.id


app.register_blueprint(routes)

if __name__ == '__main__':
    app.run(debug=True)