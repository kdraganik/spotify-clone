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
        songs = Song.query.all()
        # Use the first song from the session queue (if any), else fallback:
        queue = session.get('queue', [])
        if queue:
            song = Song.query.get(queue[0])
        else:
            song = Song.query.first()
        if song:
            current_artist = Artist.query.get(song.artist)
            current_album = Album.query.get(song.album)
        else:
            current_artist = None
            current_album = None
        # Fetch user's playlists for "Twoje playlisty"
        user_playlists = Playlist.query.filter_by(user_id=session.get('user')).all()
        return render_template('home.html', songs=songs, current_song=song, current_artist=current_artist, current_album=current_album, user_playlists=user_playlists)
    
    @app.route('/queue-song/<int:song_id>')
    @login_required
    def queue_song(song_id):
        song = Song.query.get(song_id)
        if song is None:
            return 'Song not found', 404
        # Initialize or update the session-song queue
        queue = session.get('queue', [])
        queue.append(song_id)
        session['queue'] = queue
        return redirect(url_for('index'))

    @app.route('/queue-song-next/<int:song_id>')
    @login_required
    def queue_song_next(song_id):
        song = Song.query.get(song_id)
        if song is None:
            return 'Song not found', 404
        queue = session.get('queue', [])
        queue.insert(0, song_id)
        session['queue'] = queue
        return redirect(url_for('index'))
    
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
    
    @app.route('/play-next')
    @login_required
    def play_next():
        queue = session.get('queue', [])
        if not queue:
            return "No song in queue", 404
        song_id = queue.pop(0)
        session['queue'] = queue
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
    
    @app.route('/artist/<int:artist_id>')
    @login_required
    def artist(artist_id):
        artist = Artist.query.get(artist_id)
        if artist is None:
            return 'Artist not found', 404
        albums = Album.query.filter_by(artist=artist_id).all()
        songs = Song.query.filter_by(artist=artist_id).all()
        return render_template('artist.html', artist=artist, albums=albums, songs=songs)
    
    @app.route('/artist-image/<int:artist_id>')
    @login_required
    def artist_image(artist_id):
        artist = Artist.query.get(artist_id)
        if artist is None:
            return 'Artist not found', 404
        image = io.BytesIO(artist.profile_image)
        image.seek(0)
        return send_file(
            image,
            mimetype='image/jpeg',
            as_attachment=False,
            download_name=artist.profile_image_name
        )
    
    @app.route('/album/<int:album_id>')
    @login_required
    def album(album_id):
        album_obj = Album.query.get(album_id)
        if album_obj is None:
            return 'Album not found', 404
        songs = Song.query.filter_by(album=album_id).all()
        user_id = session.get('user')
        user_playlists = Playlist.query.filter_by(user_id=user_id).all()
        return render_template('album.html', album=album_obj, songs=songs, user_playlists=user_playlists)
    
    @app.route('/album-image/<int:album_id>')
    @login_required
    def album_image(album_id):
        album = Album.query.get(album_id)
        if album is None:
            return 'Album not found', 404
        image = io.BytesIO(album.cover_image)
        image.seek(0)
        return send_file(
            image,
            mimetype='image/jpeg',
            as_attachment=False,
            download_name=album.cover_image_name
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
            profile_image = request.files.get('image')
            if not profile_image:
                print('Profile image not found')
                error = 'Profile image is required'
                return render_template('add_artist.html', error=error)
            profile_image_data = profile_image.read()
            profile_image = profile_image_data
            profile_image_name = name + '.jpg'

            artist = Artist(name=name, genre=genre, profile_image=profile_image, profile_image_name=profile_image_name)
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
    
    @app.route('/add_playlist', methods=['GET', 'POST'])
    @login_required
    def add_playlist():
        error = None
        if request.method == 'POST':
            name = request.form['name']
            user_id = session.get('user')
            playlist = Playlist(name=name, user_id=user_id)
            db.session.add(playlist)
            db.session.commit()
            return redirect(url_for('profile'))
        return render_template('add_playlist.html', error=error)

    @app.route('/profile', methods=['GET'])
    @login_required
    def profile():  
        user_id = session.get('user')
        playlists = Playlist.query.filter_by(user_id=user_id).all()
        return render_template('profile.html', playlists=playlists, user_name=User.query.get(user_id).username)

    @app.route('/add_to_playlist', methods=['POST'])
    @login_required
    def add_to_playlist():
        user_id = session.get('user')
        song_id = request.form.get('song_id')
        playlist_id = request.form.get('playlist_id')
        # Validate required fields
        if not (song_id and playlist_id):
            return "Missing song id or playlist id", 400
        song = Song.query.get(song_id)
        playlist = Playlist.query.filter_by(id=playlist_id, user_id=user_id).first()
        if not playlist:
            playlist = Playlist(name="Moja Playlista", user_id=user_id)
            db.session.add(playlist)
            db.session.commit()
        if song and song not in playlist.songs:
            playlist.songs.append(song)
            db.session.commit()
        return redirect(url_for('album', album_id=song.album))

    @app.route('/playlist/<int:playlist_id>')
    @login_required
    def view_playlist(playlist_id):
        user_id = session.get('user')
        playlist = Playlist.query.filter_by(id=playlist_id, user_id=user_id).first()
        if not playlist:
            return "Playlist not found", 404
        return render_template('playlist.html', playlist=playlist)
    
    @app.route('/remove_from_playlist', methods=['POST'])
    @login_required
    def remove_from_playlist():
        user_id = session.get('user')
        song_id = request.form.get('song_id')
        playlist_id = request.form.get('playlist_id')
        if not (song_id and playlist_id):
            return "Missing song or playlist id", 400
        playlist = Playlist.query.filter_by(id=playlist_id, user_id=user_id).first()
        if not playlist:
            return "Playlist not found", 404
        song = Song.query.get(song_id)
        if song in playlist.songs:
            playlist.songs.remove(song)
            db.session.commit()
        return redirect(url_for('view_playlist', playlist_id=playlist_id))

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'))
        
    # New route for auto playing next queued song
    @app.route('/play-next-and-redirect')
    @login_required
    def play_next_and_redirect():
        queue = session.get('queue', [])
        if not queue:
            return redirect(url_for('index'))
        song_id = queue.pop(0)
        session['queue'] = queue
        return redirect(url_for('index'))