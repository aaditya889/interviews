from flask_sqlalchemy import SQLAlchemy
from singleton import Singleton
from model.config import POSTGRES

singleton = Singleton()
current_environment = 'development'

def initialise_db_session():
  db_connection_string = f'postgresql://{POSTGRES[current_environment]["user"]}:{POSTGRES[current_environment]["password"]}\
@{POSTGRES[current_environment]["host"]}:{POSTGRES[current_environment]["port"]}/{POSTGRES[current_environment]["database"]}'
    
  print(f'Connecting to DB: {db_connection_string}')
  singleton.flask_app.config['SQLALCHEMY_DATABASE_URI'] = db_connection_string
  db = SQLAlchemy(singleton.flask_app)
  singleton.db = db
  singleton.models = {}
  with singleton.flask_app.app_context():
    db.create_all()

