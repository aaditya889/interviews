from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func
from singleton import Singleton


singleton = Singleton()
db = singleton.db


class Player(db.Model):
  __tablename__ = 'player'
  id = db.Column(db.Integer, primary_key = True)
  name = db.Column(db.String(256))
  userid = db.Column(db.String(256), unique=True)
  password_hash = db.Column(db.String(256))
  created_at = db.Column(db.TIMESTAMP, server_default=func.now())
  updated_at = db.Column(db.TIMESTAMP, server_default=func.now(), server_onupdate=func.now())


class GameState(db.Model):
	__tablename__ = 'game_state'
	id = db.Column(db.Integer, primary_key = True)
	player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
	game_type = db.Column(db.String(256))
	state = db.Column(db.JSON)
	created_at = db.Column(db.TIMESTAMP, server_default=func.now())
	updated_at = db.Column(db.TIMESTAMP, server_default=func.now(), server_onupdate=func.now())
 

class GameRoom(db.Model):
	__tablename__ = 'game_room'
	id = db.Column(db.Integer, primary_key = True)
	player_ids = db.Column(ARRAY(db.String(256)), default=[])
	leader_id = db.Column(db.String(256))
	game_type = db.Column(db.String(256))
	created_at = db.Column(db.TIMESTAMP, server_default=func.now())
	updated_at = db.Column(db.TIMESTAMP, server_default=func.now(), server_onupdate=func.now())


class PlayerSession(db.Model):
	__tablename__ = 'player_session'
	id = db.Column(db.Integer, primary_key = True)
	player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
	session_id = db.Column(db.String(256))
	created_at = db.Column(db.TIMESTAMP, server_default=func.now())
	updated_at = db.Column(db.TIMESTAMP, server_default=func.now(), server_onupdate=func.now())


singleton.models['player'] = Player
singleton.models['game_state'] = GameState
singleton.models['game_room'] = GameRoom
singleton.models['player_session'] = PlayerSession

with singleton.flask_app.app_context():
	db.create_all()
