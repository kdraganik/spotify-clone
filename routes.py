from flask import render_template, request, session, redirect, url_for
from models import db, User, Artist, Album, Song, Role
from utils import get_hash, check_hash
from datetime import datetime
from functools import wraps


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'ADMIN':
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def init_routes(app):
    @app.route('/')
    @login_required
    def index():
        return render_template('home.html')
    
    @app.route('/admin')
    @login_required
    @admin_required
    def admin():
        return render_template('admin.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        error = None
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            
            user = User.query.filter_by(email=email).first()
            if user is None:
                error = 'User not found'
            elif not check_hash(password, user.password):
                error = 'Password is incorrect'
            else:
                session['user'] = user.id
                session['role'] = user.role.name
                return redirect(url_for('index'))
        
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
            
            user = User(username=username, email=email, password=password_hash, role=Role.USER)
            db.session.add(user)
            db.session.commit()
            
            return 'User registered'
        return render_template('register.html', error=error)
    
    @app.route('/add_album', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def add_album():
        error = None
        if request.method == 'POST':
            title = request.form['title']
            artist = int(request.form['artist'])
            date = datetime.strptime(request.form['date-published'], '%Y-%m-%d').date()
            genre = request.form['genre']
            
            album = Album(title=title, artist=artist, date=date, genre=genre)
            db.session.add(album)
            db.session.commit()
            
            return 'Album recived'
        return render_template('add_album.html', error=error, artists=Artist.query.all())
    
    @app.route('/add_artist', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def add_artist():
        print(session)
        error = None
        if request.method == 'POST':
            name = request.form['name']
            genre = request.form['genre']
            
            artist = Artist(name=name, genre=genre)
            db.session.add(artist)
            db.session.commit()
            
            return 'Artist added'
        return render_template('add_artist.html', error=error)
    
    @app.route('/add_song', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def add_song():
        error = None
        if request.method == 'POST':
            title = request.form['title']
            artist = int(request.form['artist'])
            album = int(request.form['album'])
            date = request.form['date-published']
            genre = request.form['genre']
            
            song = Song(title=title, artist=artist, album=album, date=date, genre=genre)
            db.session.add(song)
            db.session.commit()
            
            return 'Album recived'
        return render_template(
            'add_album.html', 
            error=error, 
            artists=Artist.query.all(),
            albums=Album.query.all(),
        )
    
    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'))