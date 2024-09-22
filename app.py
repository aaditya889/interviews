from flask import Flask, request, jsonify
from functools import wraps
from singleton import Singleton
from model.db import initialise_db_session

# Change the location for this subroutine (fix the imports and initialisations), for now it shouldn't be changed
singleton = Singleton()
app = Flask(__name__)
singleton.flask_app = app
initialise_db_session()

from model.schemas.game import Player, PlayerSession
from model.schemas.hangman import HangmanWords
from flask_socketio import SocketIO, emit, join_room, leave_room
from model.schemas.game import GameRoom
from controllers.clients.play_game import play_hangman
from controllers.game_room import GameRoomSession

socketio = SocketIO(app)
clients = []
max_clients = 12

@socketio.on('connect')
def handle_connect():
  if len(clients) < max_clients:
    clients.append(request.sid)
    print(f'Client {request.sid} connected')
  else:
    emit('error', {'message': 'Server full'}, room=request.sid)
    return False


@socketio.on('disconnect')
def handle_disconnect():
  if request.sid in clients:
    
    game_room = GameRoom.query.filter(GameRoom.player_ids.contains([request.sid])).first()
    if game_room:
      player_ids = game_room.player_ids
      player_ids.remove(request.sid)
      GameRoom.query.filter(GameRoom.id==game_room.id).update(values={'player_ids': player_ids})
      singleton.db.session.commit()
      leave_room(game_room.id, sid=request.sid)
    
    clients.remove(request.sid)
    print(f'Client {request.sid} disconnected')


# @app.route('/broadcast', methods=['POST'])
# def broadcast_message():
#   message = request.json.get('message')
#   print(f'got a new message: {message}')
#   if message:
#     for client in clients:
#       socketio.emit('response', {'message': message}, room=client)
#     return jsonify({"message": "Broadcast sent"}), 200
#   return jsonify({"message": "No message provided"}), 400


# @app.route('/get_players', methods=['GET'])
# def get_players():
#   players = Player.query.all()
#   return jsonify([player.to_dict() for player in players]), 200


@app.route('/create_player', methods=['POST'])
def create_player():
  name = request.json.get('name')
  userid = request.json.get('userid')
  password_hash = request.json.get('password_hash')
  if name and userid and password_hash:
    player = Player(name=name, userid=userid, password_hash=password_hash)
    singleton.db.session.add(player)
    singleton.db.session.commit()
    return jsonify({"player_id": player.id}), 200
  return jsonify({"message": "Missing required fields"}), 400


@socketio.on('player_login')
def player_login(data):
  userid = data.get('userid')
  password_hash = data.get('password_hash')
  player: Player = Player.query.filter_by(userid=userid, password_hash=password_hash).first()
  if player:
    player_session = PlayerSession(player_id=player.id, session_id=request.sid)
    singleton.db.session.add(player_session)
    singleton.db.session.commit()
    emit('player_login_response', {'error': False, 'message': 'Player logged in', 'session_id': request.sid})
  else:
    emit('player_login_response', {'error': True, 'message': 'Player not found'}, room=request.sid)


@socketio.on('create_game_room')
def create_game_room():
  game_room = GameRoom(player_ids=[request.sid], leader_id=request.sid, game_type='hangman')
  singleton.db.session.add(game_room)
  singleton.db.session.commit()
  
  print(f'{request.sid} is joining room {game_room.id}')
  join_room(game_room.id, sid=request.sid)
  emit('create_game_room_response', {'error': False, 'message': 'Game room created', 'room_id': game_room.id}, room=request.sid)
  
  new_game_room = GameRoomSession(socketio, game_room.id)
  new_game_room.play_game()
  

@socketio.on('enter_game_room')
def enter_game_room(data):
  game_room_id = data.get('game_room_id')
  player_sid = data.get('player_sid')
  
  player_session = PlayerSession.query.filter_by(session_id=player_sid).first()
  if not player_session:
    emit('enter_game_room_response', {'error': True, 'message': 'Invalid player'}, room=request.sid)
    return
  
  game_room = GameRoom.query.filter_by(id=game_room_id).first()
  if game_room:
    player_ids = game_room.player_ids
    player_ids.append(player_sid)
    game_room.player_ids = player_ids
    GameRoom.query.filter(GameRoom.id==game_room_id).update(values={'player_ids': player_ids})
    singleton.db.session.commit()
    game_room = GameRoom.query.filter_by(id=game_room_id).first()
    
    print(f'{player_sid} is joining room {game_room_id}')
    join_room(game_room_id, sid=player_sid)
    emit('enter_game_room_response', {'error': False, 'message': 'Entered game room'}, room=player_sid)
  else:
    emit('enter_game_room_response', {'error': True, 'message': 'Game room not found'}, room=player_sid)



if __name__ == '__main__':
  socketio.run(app, port=7894, debug=True)