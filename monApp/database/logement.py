from ..app import db
from monApp.database.justifie import justifie
from monApp.database.couvre import couvre
from monApp.database.possede import possede

class Logement(db.Model):
    __tablename__ = 'logement'
    id_logement = db.Column(db.Integer, primary_key=True)
    adresse = db.Column(db.String(255), nullable=False, unique=True)
    type_logement = db.Column(db.String(50))
    surface = db.Column(db.Numeric(10,2))
    description = db.Column(db.Text)

    pieces = db.relationship('Piece', backref='logement', lazy='subquery', cascade="all, delete-orphan")
    sinistres = db.relationship('Sinistre', backref='logement', lazy=True)
    justificatifs = db.relationship('Justificatif', secondary=justifie, backref=db.backref('logements', lazy='subquery'), lazy='subquery')
    assureurs = db.relationship('Assureur', secondary=couvre, back_populates='logements_couverts', lazy='subquery')

    def __init__(self, adresse, type_logement=None, surface=None, description=None):
        self.adresse = adresse
        self.type_logement = type_logement
        self.surface = surface
        self.description = description

    def __repr__(self):
        return f"<Logement {self.id_logement} {self.adresse}>"