from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SECRET_KEY'] = 'LJADLKCDDFD425344dfhW'
app.config["SESSION_PERMANENT"] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gameData.db'
app.config['SQLALCHEMY_BINDS'] = {'stations': 'sqlite:///gameData.db', 'games': 'sqlite:///gameData.db'}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
sess = Session(app)
db = SQLAlchemy(app)
#  sudo gunicorn3 -w 4 --reload -b localhost:5000 denominationCounter:app