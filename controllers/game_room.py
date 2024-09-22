from singleton import Singleton
from flask_socketio import SocketIO, emit, join_room, leave_room
from controllers.hangman import Hangman
from utils import multi_thread, multi_process
from model.schemas.game import GameRoom
import random
import string

singleton = Singleton()


class GameRoomSession:
  room_id = None
  game_type = None
  socketio_obj = None
  current_player_sid = None
  players_in_room = []
  is_game_over = False
  
  def __init__(self, socketio_obj: SocketIO, room_id) -> None:
    self.room_id = room_id
    game_room_model: GameRoom = singleton.models['game_room']
    self.game_type = game_room_model.query.filter_by(id=room_id).first().game_type
    self.socketio_obj = socketio_obj
    game_room = GameRoom.query.filter_by(id=room_id).first()
    self.players_in_room = game_room.player_ids
    self.current_player_sid = self.players_in_room[0]
    
  
  def _initialise_game_room_listeners(self):
    socketio = self.socketio_obj
    @socketio.on(f'play_move_{self.room_id}')
    def play_move(data):
      print(data)
      player_sid = data.get('player_sid')
      if player_sid != self.current_player_sid:
        socketio.emit(f'error_{self.room_id}', {'message': 'Not your turn'}, room=player_sid)
        return
      move = data.get('move')
      self.game_obj.play_move(move)
      game_state = self.game_obj.get_current_state()
      self.current_player_sid = self.players_in_room[(self.players_in_room.index(self.current_player_sid) + 1) % len(self.players_in_room)]
      game_state['current_player_sid'] = self.current_player_sid
      socketio.emit(f'game_state_{self.room_id}', game_state, room=self.room_id)
    
    
    @socketio.on(f'get_game_state_{self.room_id}')
    def get_game_state(data):
      player_sid = data.get('player_sid')
      game_state = self.game_obj.get_current_state()
      game_state['current_player_sid'] = self.current_player_sid
      socketio.emit(f'game_state_{self.room_id}', game_state, room=player_sid)
    
    
    @socketio.on(f'exit_room_{self.room_id}')
    def exit_room(data):
      player_sid = data.get('player_sid')
      self.players_in_room.remove(player_sid)
      if player_sid == self.current_player_sid:
        self.current_player_sid = self.players_in_room[0]
      
      game_state = self.game_obj.get_current_state()
      game_state['current_player_sid'] = self.current_player_sid
      socketio.emit(f'game_state_{self.room_id}', game_state, room=self.room_id)
      socketio.emit(f'exit_room_{self.room_id}', {'message': 'Player has left the game'}, room=self.room_id)
      
      
    @socketio.on(f'joined_room_{self.room_id}')
    def joined_room(data):
      player_sid = data.get('player_sid')
      game_state = self.game_obj.get_current_state()
      game_state['message'] = 'Player has joined the room'
      game_state['current_player_sid'] = self.current_player_sid
      socketio.emit(f'joined_room_{self.room_id}', game_state, room=self.room_id)
      del game_state['message']
      socketio.emit(f'game_state_{self.room_id}', game_state, room=player_sid)
      
      
  @multi_thread(f'play_game_{"".join(random.choices(string.ascii_uppercase + string.digits, k=5))}')
  def play_game(self):
    if self.game_type == 'hangman':
      self.game_obj = Hangman()

    self.game_obj.load_new_game()
    self._initialise_game_room_listeners()

    while(True):
      if self.game_obj.is_game_over:
        break
      if self.current_player_sid not in self.players_in_room:
        break
      if len(self.players_in_room) == 0:
        break
      
      pass