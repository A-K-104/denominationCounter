from datetime import datetime
from flask import session
import constance
from classes.database.GameSession import GameSession

db = constance.db


class Games(db.Model):
    # to init db in terminal type: python ->from app import db->db.create_all()-> exit(). and you are set!
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean(), default=False, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_ended = db.Column(db.DateTime, nullable=True)

    session = db.Column(db.Integer, db.ForeignKey(GameSession.id))

    stationsTakeOvers = db.relationship("StationsTakeOvers", backref="Games", lazy=True)

    def __repr__(self):
        return '<Name %r>' % self.id


def checkIfInSession():
    if not ('email' in session):
        return False
    return True
