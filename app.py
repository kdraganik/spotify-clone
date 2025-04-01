from flask import Flask, render_template, request
from models import db
import os
from routes import init_routes

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///spotify_clone.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'ask234dj234fhaskj4435dhiu2y'

db.init_app(app)

# with app.app_context():
#     db.create_all()

if __name__ == '__main__':
    init_routes(app)
    app.run(debug=True)