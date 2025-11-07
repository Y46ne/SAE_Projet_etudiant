from ..app import db


class Piece(db.Model):
    __tablename__ = 'piece'
    id_piece = db.Column(db.Integer, primary_key=True)
    nom_piece = db.Column(db.String(100), nullable=False)
    surface = db.Column(db.Numeric(10,2))
    id_logement = db.Column(db.Integer, db.ForeignKey('logement.id_logement'), nullable=False)

    biens = db.relationship('Bien', backref='piece', lazy='subquery', cascade="all, delete-orphan")

    def __init__(self, nom_piece, type_piece=None, surface=None, id_logement=None):
        self.nom_piece = nom_piece
        self.surface = surface
        self.id_logement = id_logement

    def __repr__(self):
        return f"<Piece {self.id_piece} {self.nom_piece}>"