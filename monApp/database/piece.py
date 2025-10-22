from ..app import db

class Piece(db.Model):
    id_piece = db.Column(db.Integer, primary_key=True)
    nom_piece = db.Column(db.String(255))
    type_piece = db.Column(db.String(255))
    surface = db.Column(db.Float)
    etage = db.Column(db.String(50))
    id_logement = db.Column(db.Integer, db.ForeignKey('logement.id_logement'), nullable=False)
    biens = db.relationship('Bien', backref='piece', lazy=True)

    def __init__(self, nom_piece, type_piece, surface, etage, id_logement):
        self.nom_piece = nom_piece
        self.type_piece = type_piece
        self.surface = surface
        self.etage = etage
        self.id_logement = id_logement

    def __repr__(self):
        return "<Piece (%d) %s>" % (self.id_piece, self.nom_piece)