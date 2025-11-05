from ..app import db
from monApp.database.justifie import justifie
from monApp.database.couvre import couvre
from monApp.database.possede import possede


class Logement(db.Model):
    __tablename__ = 'logement'
    id_logement = db.Column(db.Integer, primary_key=True)
    adresse = db.Column(db.String(255), nullable=False)
    type_logement = db.Column(db.String(50))
    surface = db.Column(db.Numeric(10,2))
    description = db.Column(db.Text)
    
    pieces = db.relationship('Piece', backref='logement', lazy='subquery')
    sinistres = db.relationship('Sinistre', backref='logement', lazy=True)
    justificatifs = db.relationship('Justificatif', secondary=justifie, backref=db.backref('logements', lazy='subquery'), lazy='subquery')
    assureurs = db.relationship('Assureur', secondary=couvre, backref=db.backref('logements', lazy='subquery'), lazy='subquery')
    proprietaires = db.relationship('Assure', secondary=possede, backref=db.backref('logements_possedes', lazy='subquery'), lazy='subquery')

    def __init__(self, adresse, type_logement=None, surface=None, description=None):
        self.adresse = adresse
        self.type_logement = type_logement
        self.surface = surface
        self.description = description

    def __repr__(self):
        return f"<Logement {self.id_logement} {self.adresse}>"