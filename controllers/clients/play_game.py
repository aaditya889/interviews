from flask import Flask, request, jsonify
from singleton import Singleton
from socketIO_client import SocketIO
import socketio
import time
from flask_socketio import SocketIO, emit, join_room, leave_room
from controllers.clients.play_hangman import play_hangman_client


singleton = Singleton()
app = singleton.flask_app
is_connected = True
is_logged_in = False
is_waiting = False
player_sid = None


@app.cli.command('play_hangman')
def play_hangman():
  sio = socketio.Client()
  sio.connect('http://localhost:7894')

  @sio.on('response')
  def response(data):
    print('received a new message!')
    print(data)

  @sio.on('player_login_response')
  def player_login_response(data):
    global is_logged_in, is_waiting, player_sid
    is_waiting = False
    
    if data.get('error') == False:
      is_logged_in = True
      player_sid = data.get('session_id')
      print('Logged in successfully')
    else:
      is_logged_in = False
      print('Login failed')

  @sio.on('create_game_room_response')
  def create_game_room_response(data):
    global is_waiting
    is_waiting = False
    if data.get('error') == False:
      print('Game room created successfully: ')
      print(data)
    else:
      print('Game room creation failed')

  @sio.on('enter_game_room_response')
  def enter_game_room_response(data):
    global is_waiting
    is_waiting = False
    print('Received enter game room response')
    print(data)
    if data.get('error') == False:
      print('Entered game room successfully')
    else:
      print('Failed to enter game room')


  print('Type \'exit\' or CTRL+c to disconnect')
  global is_connected, is_logged_in, is_waiting
  
  while is_connected:
    if not is_logged_in:
      print('Please login first (CTRL+c to exit)')
      userid = input('Enter userid: ')
      password_hash = input('Enter password_hash: ')
      is_waiting = True
      sio.emit('player_login', {'userid': userid, 'password_hash': password_hash})
      while is_waiting:
        time.sleep(1)
      
    if is_logged_in:
      print("Choose an action:")
      print("1. Create Game Room")
      print("2. Join Game Room")
      print("3. Exit")

      choice = input("Enter your choice: ")

      if choice == '1':
        is_waiting = True
        sio.emit('create_game_room')
        while is_waiting:
          time.sleep(1)
          
      elif choice == '2':
        room_id = input("Enter room id to join: ")
        is_waiting = True
        print('Trying to join game room ', room_id, ', player_sid: ', player_sid)
        sio.emit('enter_game_room', {'game_room_id': room_id, 'player_sid': player_sid})
        while is_waiting:
          time.sleep(1)
        
        @sio.on(f'joined_room_{room_id}')
        def joined_room(data):
          global is_connected
          print('Joined room')
          print(data)
          game_type = data.get('game_type')
          print(f'Joined room {room_id} successfully. Currently playing: {game_type}...')
          print('You can now play the game!')
          if game_type == 'hangman':
            play_hangman_client(sio, room_id, player_sid)
          sio.disconnect()
          is_connected = False
          exit(0)
        time.sleep(1)
        
        print('Joining room...')
        sio.emit(f'joined_room_{room_id}', {'player_sid': player_sid})
        time.sleep(1)
        while True:
          pass
        
        break
      
      elif choice == '3':
        is_connected = False
        is_logged_in = False
        sio.disconnect()
        exit(0)
      else:
        print("Invalid choice. Please try again.")
        
  sio.disconnect()