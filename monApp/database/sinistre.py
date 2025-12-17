from ..app import db
from monApp.database.impacte import impacte


class Sinistre(db.Model):
    __tablename__ = 'sinistre'
    id_sinistre = db.Column(db.Integer, primary_key=True)
    date_sinistre = db.Column(db.Date, nullable=False)
    type_sinistre = db.Column(db.String(100))
    description = db.Column(db.Text)
    montant_estime = db.Column(db.Numeric(10,2))
    numero_sinistre = db.Column(db.String(50), unique=True, nullable=False)

    id_logement = db.Column(db.Integer, db.ForeignKey('logement.id_logement'), nullable=False)

    def __init__(self, date_sinistre, type_sinistre, description, numero_sinistre, id_logement, montant_estime=None):
        self.date_sinistre = date_sinistre
        self.type_sinistre = type_sinistre
        self.description = description
        self.numero_sinistre = numero_sinistre
        self.id_logement = id_logement

    def __repr__(self):
        return f"<Sinistre {self.id_sinistre} {self.numero_sinistre}>"