from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import *


app = Flask(__name__)

ENV = 'dev'

if ENV == 'prod':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:@localhost/postgres'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://klrefwtxuudiqb:e91127fd686e6cd4e578798df2dd69a1f8f8d7fc383bfd39610897cacb6a97db@ec2-54-157-16-196.compute-1.amazonaws.com:5432/d1gd12496no4uv'

 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Player(db.Model):
    __tablename__ = 'stats'
    name = db.Column(db.VARCHAR(40))
    id = db.Column(db.INT, primary_key = True)
    ppg = db.Column(db.VARCHAR(10))
    apg = db.Column(db.VARCHAR(10))
    rpg = db.Column(db.VARCHAR(10))
    url = db.Column(db.VARCHAR(100))

    def __init__(self, name, ppg, apg, rpg, url):
        self.name = name
        self.ppg = ppg
        self.apg = apg
        self.rpg = rpg
        self.url = url


@app.route('/', methods = ['POST', 'GET'])

def index():

    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug = True)