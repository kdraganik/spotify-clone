from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'
    
class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    artist = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    album = db.Column(db.Integer, db.ForeignKey('album.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    genre = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f'<Song {self.title}>'
    
class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    artist = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    genre = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f'<Album {self.title}>'
    
class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    genre = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f'<Artist {self.name}>'