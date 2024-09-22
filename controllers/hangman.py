from controllers.games import Games
from sqlalchemy.sql import func
from singleton import Singleton
import string
singleton = Singleton()


class Hangman():
  current_word = None
  total_turns = 5
  current_turn = 0
  letters_left = None
  correct_letters = None
  is_game_over = False
  game_model = singleton.models['hangman_words']
  
  
  def __init__(self):
    self.correct_letters = []
    self.letters_left = list(string.ascii_lowercase)
    pass
  
  
  def load_new_game(self):
    with singleton.flask_app.app_context():
      self.current_word = self.game_model.query.order_by(func.random()).first().word
    
    
  def play_move(self, letter):
    if letter in self.letters_left:
      if letter in self.current_word:
        self.correct_letters.append(letter)
      else:
        self.current_turn += 1
      self.letters_left.remove(letter)
    return self._check_game_over()


  def _check_game_over(self):
    if self.current_turn >= self.total_turns:
      self.is_game_over = True
      return 'lose'
    if all([i in self.correct_letters for i in self.current_word]):
      self.is_game_over = True
      return 'win'
    return 'continue'
  
  
  def get_current_state(self):
    remaining_string = ' '.join([i if i in self.correct_letters else '_' for i in self.current_word])
    remaining_tries = self.total_turns - self.current_turn
    return {
      'game_type': 'hangman',
      'remaining_string': remaining_string,
      'remaining_tries': remaining_tries,
      'game_over': self.is_game_over
    }
  
  
  def load_game_from_state(self, state):
    self.current_word = state['current_word']
    self.total_turns = state['total_turns']
    self.current_turn = state['current_turn']
    self.letters_left = state['letters_left']
    self.correct_letters = state['correct_letters']
    return self._check_game_over()

    
  