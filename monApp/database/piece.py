from ..app import db


class Piece(db.Model):
    __tablename__ = 'piece'
    id_piece = db.Column(db.Integer, primary_key=True)
    nom_piece = db.Column(db.String(100), nullable=False)
    type_piece = db.Column(db.String(50))
    surface = db.Column(db.Numeric(10,2))
    etage = db.Column(db.Integer)
    id_logement = db.Column(db.Integer, db.ForeignKey('logement.id_logement'), nullable=False)

    biens = db.relationship('Bien', backref='piece', lazy='subquery')

    def __init__(self, nom_piece, type_piece=None, surface=None, etage=None, id_logement=None):
        self.nom_piece = nom_piece
        self.type_piece = type_piece
        self.surface = surface
        self.etage = etage
        self.id_logement = id_logement

    def __repr__(self):
        return f"<Piece {self.id_piece} {self.nom_piece}>"