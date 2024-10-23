from datetime import datetime
from flask import session
import constance

db = constance.db


class GameSession(db.Model):
    # to init db in terminal type: python ->from app import db->db.create_all()-> exit(). and you are set!
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    active = db.Column(db.Boolean(), default=False, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    bonus_minimum_hold = db.Column(db.Integer(), default=20, nullable=False)

    games = db.relationship("Games", backref="GameSession", lazy=True)
    teams = db.relationship("Teams", backref="GameSession", lazy=True)
    stations = db.relationship("Stations", backref="GameSession", lazy=True)

    def __repr__(self):
        return '<Name %r>' % self.id


def checkIfInSession():
    if not ('email' in session):
        return False
    return True
