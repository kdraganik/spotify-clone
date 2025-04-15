from flask_sqlalchemy import SQLAlchemy
from enum import Enum

db = SQLAlchemy()

class Role(Enum):
    USER = 1
    ADMIN = 2

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    role = db.Column(db.Enum(Role), nullable=False)

    def __repr__(self):
        return f'<User {self.username}, Role: {self.role}>'
    
class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    artist = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    album = db.Column(db.Integer, db.ForeignKey('album.id'), nullable=False)
    genre = db.Column(db.String(80), nullable=False)
    audio_file_name = db.Column(db.String(80), nullable=False)
    audio_file = db.Column(db.LargeBinary, nullable=False)

    def __repr__(self):
        return f'<Song {self.title}>'
    
class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    artist = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    genre = db.Column(db.String(80), nullable=False)
    cover_image_name = db.Column(db.String(80), nullable=True)
    cover_image = db.Column(db.LargeBinary, nullable=True)

    def __repr__(self):
        return f'<Album {self.title}>'
    
class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    genre = db.Column(db.String(80), nullable=False)
    profile_image_name = db.Column(db.String(80), nullable=True)
    profile_image = db.Column(db.LargeBinary, nullable=True)

    def __repr__(self):
        return f'<Artist {self.name}>'
    
playlist_song = db.Table('playlist_song',
    db.Column('playlist_id', db.Integer, db.ForeignKey('playlist.id'), primary_key=True),
    db.Column('song_id', db.Integer, db.ForeignKey('song.id'), primary_key=True)
)

class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    songs = db.relationship('Song', secondary=playlist_song, lazy='subquery', backref=db.backref('playlists', lazy=True))

    def __repr__(self):
        return f'<Playlist {self.name}>'