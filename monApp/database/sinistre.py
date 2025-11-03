from ..app import db
from . import impacte


class Sinistre(db.Model):
    __tablename__ = 'sinistre'
    id_sinistre = db.Column(db.Integer, primary_key=True)
    date_sinistre = db.Column(db.Date, nullable=False)
    type_sinistre = db.Column(db.String(100))
    description = db.Column(db.Text)
    numero_sinistre = db.Column(db.String(50), unique=True, nullable=False)

    # Relations
    biens = db.relationship('Bien', secondary=impacte, lazy='subquery', backref=db.backref('sinistres_assoc', lazy='subquery'))

    def __init__(self, date_sinistre, numero_sinistre, type_sinistre=None, description=None):
        self.date_sinistre = date_sinistre
        self.type_sinistre = type_sinistre
        self.description = description
        self.numero_sinistre = numero_sinistre

    def __repr__(self):
        return f"<Sinistre {self.id_sinistre} {self.numero_sinistre}>"