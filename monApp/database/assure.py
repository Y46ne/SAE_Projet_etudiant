from ..app import db
from . import possede
from datetime import date


class Assure(db.Model):
    __tablename__ = 'assure'
    id_assure = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100))
    prenom = db.Column(db.String(100))
    date_naissance = db.Column(db.Date)
    email = db.Column(db.String(100), db.ForeignKey('user.Login'), unique=True)
    id_assureur = db.Column(db.Integer, db.ForeignKey('assureur.id_assureur'), nullable=False)
    telephone = db.Column(db.String(20))

    # Relations
    logements = db.relationship('Logement', secondary=possede, backref=db.backref('proprietaires', lazy='subquery'), lazy='subquery')

    def __init__(self, nom, prenom, date_naissance, email, id_assureur, telephone=None):
        self.nom = nom
        self.prenom = prenom
        self.date_naissance = date_naissance
        self.email = email
        self.telephone = telephone
        self.id_assureur = id_assureur

    def __repr__(self):
        return f"<Assure {self.id_assure} {self.prenom} {self.nom}>"