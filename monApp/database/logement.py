from ..app import db

class Logement(db.Model):
    id_logement = db.Column(db.Integer, primary_key=True)
    adresse = db.Column(db.String(255))
    type_logement = db.Column(db.String(255))
    surface = db.Column(db.Integer)
    description = db.Column(db.String(255))
    id_assure = db.Column(db.Integer, db.ForeignKey('assure.id_assure'), nullable=False)
    pieces = db.relationship('Piece', backref='logement', lazy=True)

    def __init__(self, adresse, type_logement, surface, description, id_assure):
        self.adresse = adresse
        self.type_logement = type_logement
        self.surface = surface
        self.description = description
        self.id_assure = id_assure

    def __repr__(self):
        return "<Logement (%d) %s>" % (self.id_logement, self.adresse)