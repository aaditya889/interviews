from socketio import Client as socketio_client
import time


def play_hangman_client(sio_obj: socketio_client, room_id, player_sid):
  is_playing = True
  
  @sio_obj.on(f'game_state_{room_id}')
  def game_state(data):
    print('Game state received')
    print(data)
    print('My Data: ')
    print(f'room_id: {room_id}, player_sid: {player_sid}')
    if data.get('game_over'):
      print('Game over')
      sio_obj.emit(f'exit_room_{room_id}', {'player_sid': player_sid})
      is_playing = False
      return
    if data.get('current_player_sid') == player_sid:
      print('Your turn')
      move = input('Enter your move: ')
      sio_obj.emit(f'play_move_{room_id}', {'player_sid': player_sid, 'move': move})
    else:
      print('Opponent\'s turn')
  
  @sio_obj.on(f'error_{room_id}')
  def error(data):
    print('Error: ')
    print(data)
  
  @sio_obj.on(f'exit_room_{room_id}')
  def exit_room(data):
    print('Exiting room')
    print(data)
    sio_obj.disconnect()
  
  @sio_obj.on(f'joined_room_{room_id}')
  def joined_room(data):
    print('Joined room')
    print(data)
  
  while is_playing:
    pass