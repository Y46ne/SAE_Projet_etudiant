from ..app import db
from datetime import date
from monApp.database.possede import possede


class Assure(db.Model):
    __tablename__ = 'assure'
    id_assure = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    date_naissance = db.Column(db.Date)
    email = db.Column(db.String(255), db.ForeignKey('user.Login'), unique=True, nullable=False)
    mdp_assure = db.Column(db.String(255), nullable=False)
    telephone = db.Column(db.String(20))
    id_assureur = db.Column(db.Integer, db.ForeignKey('assureur.id_assureur'), nullable=False)

    # Relations
    logements = db.relationship('Logement', secondary=possede, backref=db.backref('assures', lazy='subquery'), lazy='subquery')

    def __init__(self, nom, prenom, date_naissance, email, mdp_assure, id_assureur, telephone=None):
        self.nom = nom
        self.prenom = prenom
        self.date_naissance = date_naissance
        self.email = email
        self.mdp_assure = mdp_assure
        self.telephone = telephone
        self.id_assureur = id_assureur

    def __repr__(self):
        return f"<Assure {self.id_assure} {self.prenom} {self.nom}>"


def get_tous_les_assures():
    return Assure.query.all()
