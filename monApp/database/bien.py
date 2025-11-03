from ..app import db
from . import impacte


class Bien(db.Model):
    __tablename__ = 'bien'
    id_bien = db.Column(db.Integer, primary_key=True)
    nom_bien = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    categorie = db.Column(db.String(100))
    date_achat = db.Column(db.Date)
    prix_achat = db.Column(db.Numeric(10,2))
    etat = db.Column(db.String(50))
    valeur_actuelle = db.Column(db.Numeric(10,2))
    id_piece = db.Column(db.Integer, db.ForeignKey('piece.id_piece'), nullable=False)
    id_justificatif = db.Column(db.Integer, db.ForeignKey('justificatif.id_justificatif'))

    # Relations
    justificatifs = db.relationship('Justificatif', backref='bien', lazy='subquery')
    justificatif_principal = db.relationship('Justificatif', foreign_keys=[id_justificatif], uselist=False)
    sinistres = db.relationship('Sinistre', secondary=impacte, lazy='subquery', backref=db.backref('biens', lazy='subquery'))

    def __init__(self, nom_bien, id_piece, description=None, categorie=None, date_achat=None, prix_achat=None, etat=None, valeur_actuelle=None, id_justificatif=None):
        self.nom_bien = nom_bien
        self.description = description
        self.categorie = categorie
        self.date_achat = date_achat
        self.prix_achat = prix_achat
        self.etat = etat
        self.valeur_actuelle = valeur_actuelle
        self.id_piece = id_piece
        self.id_justificatif = id_justificatif

    def __repr__(self):
        return f"<Bien {self.id_bien} {self.nom_bien}>"