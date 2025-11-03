from ..app import db

class Sinistre(db.Model):
    id_sinistre = db.Column(db.Integer, primary_key=True)
    date_sinistre = db.Column(db.Date)
    type_sinistre = db.Column(db.String(100))
    description = db.Column(db.String(255))
    montant_estime = db.Column(db.Float)
    numero_sinistre = db.Column(db.String(100))
    id_logement = db.Column(db.Integer, db.ForeignKey('logement.id_logement'), nullable=False)

    def __init__(self, date_sinistre, type_sinistre, description, numero_sinistre, id_logement, montant_estime=None):
        self.date_sinistre = date_sinistre
        self.type_sinistre = type_sinistre
        self.description = description
        self.montant_estime = montant_estime
        self.numero_sinistre = numero_sinistre
        self.id_logement = id_logement

    def __repr__(self):
        return "<Sinistre (%d) %s>" % (self.id_sinistre, self.numero_sinistre)