from flask import render_template, request, session, redirect, url_for, send_file
from models import db, User, Artist, Album, Song, Role, Playlist
from utils import get_hash, check_hash
from datetime import datetime
from functools import wraps
import io


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
        song = Song.query.first()
        if song is None:
            return render_template('home.html')
        song_id = song.id
        return render_template('home.html', song_id=song_id)
    
    @app.route('/play/<int:song_id>')
    @login_required
    def play(song_id):
        song = Song.query.get(song_id)
        if song is None:
            return 'Song not found', 404
        audio_file = io.BytesIO(song.audio_file)
        audio_file.seek(0)
        return send_file(
            audio_file,
            mimetype='audio/mp3',
            as_attachment=True,
            download_name=song.audio_file_name
        )
    
    @app.route('/admin')
    @login_required
    @admin_required
    def admin():
        return render_template(
            'admin.html', 
            artists=Artist.query.all(),
            albums=Album.query.all(),
            songs=Song.query.all(),
        )
    
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
            
            user = User(username=username, email=email, password=password_hash, role=Role.ADMIN)
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
            cover_image = request.files.get('cover_image')
            if not cover_image:
                print('Cover image not found')
                error = 'Cover image is required'
                return render_template('add_album.html', error=error, artists=Artist.query.all())
            cover_image_data = cover_image.read()
            cover_image = cover_image_data
            cover_image_name = title + '.jpg'
            
            album = Album(title=title, artist=artist, date=date, genre=genre, cover_image=cover_image, cover_image_name=cover_image_name)

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
            genre = request.form['genre']
            audio_file = request.files.get('audio_file')
            if not audio_file:
                print('Audio file not found')
                error = 'Audio file is required'
                return render_template('add_song.html', error=error, artists=Artist.query.all(), albums=Album.query.all())
            audio_file_name = title + '.mp3'
            audio_file_data = audio_file.read()
            audio_file = audio_file_data
            
            song = Song(title=title, artist=artist, album=album, genre=genre, audio_file_name = audio_file_name, audio_file=audio_file)
            db.session.add(song)
            db.session.commit()
            
            return 'Song recived'
        return render_template(
            'add_song.html', 
            error=error, 
            artists=Artist.query.all(),
            albums=Album.query.all(),
        )

    @app.route('/profile', methods=['GET'])
    @login_required
    def profile():  
        user_id = session.get('user')
        playlists = Playlist.query.filter_by(user_id=user_id).all()
        return render_template('profile.html', playlists=playlists, user_name=User.query.get(user_id).username)

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'))