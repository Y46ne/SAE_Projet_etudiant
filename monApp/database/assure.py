from ..app import db
from . import possede
from datetime import date


class Assure(db.Model):
    __tablename__ = 'assure'
    id_assure = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    date_naissance = db.Column(db.Date)
    email = db.Column(db.String(255), unique=True, nullable=False)
    mdp_assure = db.Column(db.String(255), nullable=False)
    telephone = db.Column(db.String(20))
    id_assureur = db.Column(db.Integer, db.ForeignKey('assureur.id_assureur'))

    # Relations
    logements = db.relationship('Logement', secondary=possede, backref=db.backref('proprietaires', lazy='subquery'), lazy='subquery')

    def __init__(self, nom, prenom, email, mdp_assure, date_naissance=None, telephone=None, id_assureur=None):
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.mdp_assure = mdp_assure
        self.date_naissance = date_naissance
        self.telephone = telephone
        self.id_assureur = id_assureur

    def __repr__(self):
        return f"<Assure {self.id_assure} {self.prenom} {self.nom}>"