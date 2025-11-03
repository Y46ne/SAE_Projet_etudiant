from ..app import db
from . import possede, couvre, justifie


class Logement(db.Model):
    __tablename__ = 'logement'
    id_logement = db.Column(db.Integer, primary_key=True)
    adresse = db.Column(db.String(255))
    type_logement = db.Column(db.String(255))
    surface = db.Column(db.Integer)
    description = db.Column(db.String(255))
    id_assure = db.Column(db.Integer, db.ForeignKey('assure.id_assure'), nullable=False)

    # Relations
    pieces = db.relationship('Piece', backref='logement', lazy='subquery')
    sinistres = db.relationship('Sinistre', backref='logement', lazy=True)
    justificatifs = db.relationship('Justificatif', secondary=justifie, backref=db.backref('logements', lazy='subquery'), lazy='subquery')
    assureurs = db.relationship('Assureur', secondary=couvre, backref=db.backref('logements', lazy='subquery'), lazy='subquery')
    proprietaires = db.relationship('Assure', secondary=possede, backref=db.backref('logements', lazy='subquery'), lazy='subquery')

    def __init__(self, adresse, type_logement=None, surface=None, description=None):
        self.adresse = adresse
        self.type_logement = type_logement
        self.surface = surface
        self.description = description

    def __repr__(self):
        return f"<Logement {self.id_logement} {self.adresse}>"