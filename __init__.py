from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import constance
from routes.basicRoutsHandling import basic_routs_handling

app = Flask(__name__)
app.config['SECRET_KEY'] = 'LJADLKCDDFD425344dfhW'
app.config["SESSION_PERMANENT"] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gameData.db'
app.config['SQLALCHEMY_BINDS'] = {'stations': 'sqlite:///gameData.db', 'games': 'sqlite:///gameData.db'}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# db = constance.db
# app = constance.app
# sess = constance.sess
# app.register_blueprint(basic_routs_handling)


@app.before_first_request
def create_tables():
    db.create_all()


if __name__ == "__main__":
    app.run()
