from ..app import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    Login = db.Column(db.String(100), primary_key=True)
    Password = db.Column(db.String(100))
    assure_profile = db.relationship('Assure', backref='user_account', uselist=False, cascade="all, delete-orphan")
    assureur_profile = db.relationship('Assureur', backref='user_account', uselist=False, cascade="all, delete-orphan")
 
    def __init__(self, Login, Password):
        self.Login = Login
        self.Password = Password

    def __repr__(self):
        return "<User %s>" % self.Login

    def get_id(self):
        return self.Login
    
    @property
    def id_assure(self):
        if self.assure_profile:
            return self.assure_profile.id_assure
        return None

    @property
    def is_assureur(self):
        return self.assureur_profile is not None
