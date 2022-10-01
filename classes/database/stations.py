from datetime import datetime
from flask import session

import constance
from classes.database.GameSession import GameSession

db = constance.db


class Stations(db.Model):
    # to init db in terminal type: python ->from app import db->db.create_all()-> exit(). and you are set!
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    point = db.Column(db.Integer(), default=0, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    connected = db.Column(db.Boolean, default=False, nullable=False)
    last_ping = db.Column(db.DateTime, default=datetime.utcnow)
    session = db.Column(db.Integer, db.ForeignKey(GameSession.id))


    def __repr__(self):
        return '<Name %r>' % self.id


def checkIfInSession():
    if not ('email' in session):
        return False
    return True
