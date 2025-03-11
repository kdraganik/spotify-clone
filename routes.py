from flask import render_template, request
from models import db, User, Artist, Album, Song
from utils import get_hash, check_hash

def init_routes(app):
    @app.route('/')
    def index():
        return render_template('home.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        error = None
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']

            user = User.query.filter_by(email=email).first()
            if user is None:
                error = 'User not found'
            elif check_hash(password, user.password):
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
            
            password_hash = get_hash(password)

            user = User(username=username, email=email, password=password_hash)
            db.session.add(user)
            db.session.commit()

            return 'User registered'
        return render_template('register.html', error=error)
    
    @app.route('/add_song', methods=['GET', 'POST'])
    def add_song():
        error = None
        if request.method == 'POST':
            title = request.form['title']
            artist = request.form['artist']
            album = request.form['album']
            date = request.form['date']
            genre = request.form['genre']

            return 'Song added'
        return render_template('add_song.html', error=error)
    
    @app.route('/add_album', methods=['GET', 'POST'])
    def add_album():
        error = None
        if request.method == 'POST':
            title = request.form['title']
            artist = request.form['artist']
            date = request.form['date']
            genre = request.form['genre']

            # Add album to database

            return 'Album added'
        return render_template('add_album.html', error=error)
    
    @app.route('/add_artist', methods=['GET', 'POST'])
    def add_artist():
        error = None
        if request.method == 'POST':
            name = request.form['name']
            genre = request.form['genre']

            artist = Artist(name=name, genre=genre)
            db.session.add(artist)
            db.session.commit()

            return 'Artist added'
        return render_template('add_artist.html', error=error)