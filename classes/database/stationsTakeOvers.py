from datetime import datetime
from flask import session
import constance
from classes.database.Games import Games

db = constance.db


class StationsTakeOvers(db.Model):
    # to init db in terminal type: python ->from app import db->db.create_all()-> exit(). and you are set!
    id = db.Column(db.Integer, primary_key=True)
    stationId = db.Column(db.Integer, nullable=False)
    teamId = db.Column(db.Integer, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    game = db.Column(db.Integer, db.ForeignKey(Games.id))

    def __repr__(self):
        return '<Name %r>' % self.id

