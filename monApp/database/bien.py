from ..app import db
from monApp.database.impacte import impacte


class Bien(db.Model):
    __tablename__ = 'bien'
    id_bien = db.Column(db.Integer, primary_key=True)
    nom_bien = db.Column(db.String(255), nullable=False)
    categorie = db.Column(db.String(100))
    date_achat = db.Column(db.Date)
    prix_achat = db.Column(db.Float)
    etat = db.Column(db.String(100))

    id_piece = db.Column(db.Integer, db.ForeignKey('piece.id_piece'), nullable=False)
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
        return "<Bien (%d) %s>" % (self.id_bien, self.nom_bien)