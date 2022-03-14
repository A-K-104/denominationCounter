from datetime import datetime
from flask import session
import __init__

db = __init__.db


class Stations(db.Model):
    # to init db in terminal type: python ->from app import db->db.create_all()-> exit(). and you are set!
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    point = db.Column(db.Integer(), default=0, nullable=False)
    team = db.Column(db.Integer(), default=-1, nullable=False)
    take_over_time = db.Column(db.DateTime, default=datetime.utcnow)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Name %r>' % self.id


def checkIfInSession():
    if not ('email' in session):
        return False
    return True
