from datetime import datetime
import uuid
import bcrypt
from flask import session
from sqlalchemy.dialects.postgresql import UUID
import constance

db = constance.db


class Games(db.Model):
    # to init db in terminal type: python ->from app import db->db.create_all()-> exit(). and you are set!
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    points = db.Column(db.JSON(),default={}, nullable=True)
    active = db.Column(db.Boolean(), default=False, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Name %r>' % self.id


def checkIfInSession():
    if not ('email' in session):
        return False
    return True
