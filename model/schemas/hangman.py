from sqlalchemy import String, ARRAY
from sqlalchemy.sql import func
from singleton import Singleton


singleton = Singleton()
db = singleton.db


class HangmanWords(db.Model):
  __tablename__ = 'hangman_words'
  id = db.Column(db.Integer, primary_key = True)
  word = db.Column(db.String(256))
  created_at = db.Column(db.TIMESTAMP, server_default=func.now())
  updated_at = db.Column(db.TIMESTAMP, server_default=func.now(), server_onupdate=func.now())


singleton.models['hangman_words'] = HangmanWords
with singleton.flask_app.app_context():
	db.create_all()
