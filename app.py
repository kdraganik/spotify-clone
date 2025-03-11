from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///spotify_clone.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def hash(password):
    return password

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user is None:
            error = 'User not found'
        elif user.password != hash(password):
            error = 'Password is incorrect'
        else:
            return 'Logged in'

    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password_confirm = request.form['confirm_password']

        if password != password_confirm:
            error = 'Passwords do not match'
            return render_template('register.html', error=error)
        
        password_hash = hash(password)

        user = User(username=username, email=email, password=password_hash)
        db.session.add(user)
        db.session.commit()

        return 'User registered'
    return render_template('register.html', error=error)

# with app.app_context():
#     db.create_all()

if __name__ == '__main__':
    app.run(debug=True)