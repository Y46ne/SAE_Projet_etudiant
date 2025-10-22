from ..app import db

class Sinistre(db.Model):
    id_sinistre = db.Column(db.Integer, primary_key=True)
    date_sinistre = db.Column(db.String(100))
    type_sinistre = db.Column(db.String(100))
    description = db.Column(db.String(255))
    montant_estime = db.Column(db.Float)
    numero_sinistre = db.Column(db.String(100))

    def __init__(self, date_sinistre, type_sinistre, description, montant_estime, numero_sinistre):
        self.date_sinistre = date_sinistre
        self.type_sinistre = type_sinistre
        self.description = description
        self.montant_estime = montant_estime
        self.numero_sinistre = numero_sinistre

    def __repr__(self):
        return "<Sinistre (%d) %s>" % (self.id_sinistre, self.numero_sinistre)