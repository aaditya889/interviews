from singleton import Singleton

singleton = Singleton()


class Games:
  
  def __init__(self, game_name) -> None:
    self.game_name = game_name
    self.game_model = singleton.models[game_name]
    self.game_room_model = singleton.models['game_room']
    self.player_model = singleton.models['player']
  
  
  def create_game_room(self, player_ids, leader_id):
    game_room = self.game_room_model(player_ids=player_ids, leader_id=leader_id, game_type=self.game_name)
    singleton.db.session.add(game_room)
    singleton.db.session.commit()
    return game_room.id
  
  
  def get_game_room(self, game_room_id):
    return self.game_room_model.query.filter_by(id=game_room_id).first()
  
  
  def get_game_rooms(self, player_id):
    return self.game_room_model.query.filter(self.game_room_model.player_ids.contains([player_id])).all()
  
  
  def get_player(self, player_id):
    return self.player_model.query.filter_by(id=player_id).first()
  
  
  def create_player(self, name, userid, password_hash):
    player = self.player_model(name=name, userid=userid, password_hash=password_hash)
    singleton.db.session.add(player)
    singleton.db.session.commit()
    return player.id
  
  
  def get_game_state(self, player_id):
    return self.game_model.query.filter_by(player_id=player_id).first()
  
  
  def save_game_state(self, player_id, state):
    game_state = self.game_model(player_id=player_id, state=state)
    singleton.db.session.add(game_state)
    singleton.db.session.commit()
    
  
  def update_game_state(self, player_id, state):
    game_state = self.game_model.query.filter_by(player_id=player_id).first()
    game_state.state = state
    singleton.db.session.commit()
  
  
  def delete_game_state(self, player_id):
    game_state = self.game_model.query.filter_by(player_id=player_id).first()
    singleton.db.session.delete(game_state)
    singleton.db.session.commit()
    
  
  def load_game_from_state(self, state):
    pass
  
  
  def get_current_state(self):
    pass
  
  
  def play_move(self, move):
    pass
  
  
  def _check_game_over(self):
    pass
