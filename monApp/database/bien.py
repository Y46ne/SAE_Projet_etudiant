from ..app import db

impacte = db.Table('impacte',
    db.Column('id_bien', db.Integer, db.ForeignKey('bien.id_bien'), primary_key=True),
    db.Column('id_sinistre', db.Integer, db.ForeignKey('sinistre.id_sinistre'), primary_key=True),
    db.Column('degat_estime', db.Float),
    db.Column('description_degats', db.String(255)),
    db.Column('partie_impactee', db.String(255))
)

class Bien(db.Model):
    id_bien = db.Column(db.Integer, primary_key=True)
    nom_bien = db.Column(db.String(255))
    description = db.Column(db.String(255))
    categorie = db.Column(db.String(100))
    date_achat = db.Column(db.String(100))
    prix_achat = db.Column(db.Float)
    etat = db.Column(db.String(100))
    valeur_actuelle = db.Column(db.Float)
    id_piece = db.Column(db.Integer, db.ForeignKey('piece.id_piece'), nullable=False)
    justificatifs = db.relationship('Justificatif', backref='bien', lazy=True)
    sinistres = db.relationship('Sinistre', secondary=impacte, lazy='subquery',
                                backref=db.backref('biens', lazy=True))

    def __init__(self, nom_bien, description, categorie, date_achat, prix_achat, etat, valeur_actuelle, id_piece):
        self.nom_bien = nom_bien
        self.description = description
        self.categorie = categorie
        self.date_achat = date_achat
        self.prix_achat = prix_achat
        self.etat = etat
        self.valeur_actuelle = valeur_actuelle
        self.id_piece = id_piece

    def __repr__(self):
        return "<Bien (%d) %s>" % (self.id_bien, self.nom_bien)
