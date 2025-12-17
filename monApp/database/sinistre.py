from ..app import db
from monApp.database.impacte import impacte
from datetime import date


class Sinistre(db.Model):
    __tablename__ = 'sinistre'
    id_sinistre = db.Column(db.Integer, primary_key=True)
    date_sinistre = db.Column(db.Date, nullable=False)
    type_sinistre = db.Column(db.String(100))
    description = db.Column(db.Text)
    montant_estime = db.Column(db.Numeric(10,2))
    montant_final = db.Column(db.Numeric(10, 2), nullable=True)
    numero_sinistre = db.Column(db.String(50), unique=True, nullable=False)
    date_declaration = db.Column(db.Date, nullable=False, default=date.today)
    statut = db.Column(db.String(50), nullable=False, default='Déclaré')

    id_logement = db.Column(db.Integer, db.ForeignKey('logement.id_logement'), nullable=False)

    def __init__(self, date_sinistre, type_sinistre, description, numero_sinistre, id_logement, montant_estime=None, montant_final=None, date_declaration=None, statut='Déclaré'):
        self.date_sinistre = date_sinistre
        self.type_sinistre = type_sinistre
        self.description = description
        self.numero_sinistre = numero_sinistre
        self.id_logement = id_logement
        self.montant_estime = montant_estime
        self.montant_final = montant_final
        if date_declaration is None:
            self.date_declaration = date.today()
        else:
            self.date_declaration = date_declaration
        self.statut = statut

    def __repr__(self):
        return f"<Sinistre {self.id_sinistre} {self.numero_sinistre}>"