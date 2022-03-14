from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import constance
from routes.basicRoutsHandling import basic_routs_handling

app = constance.app
db = constance.db
sess = constance.sess
app.register_blueprint(basic_routs_handling)


@app.before_first_request
def create_tables():
    db.create_all()


if __name__ == "__main__":
    app.run()
