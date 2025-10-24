from ..app import db

class Assure(db.Model):
    id_assure = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100))
    prenom = db.Column(db.String(100))
    date_naissance = db.Column(db.Date)
    email = db.Column(db.String(100), db.ForeignKey('user.Login'), unique=True)
    id_assureur = db.Column(db.Integer, db.ForeignKey('assureur.id_assureur'), nullable=False)
    telephone = db.Column(db.String(20))
    logements = db.relationship('Logement', backref='assure', lazy=True)

    def __init__(self, nom, prenom, date_naissance, email, telephone, id_assureur):
        self.nom = nom
        self.prenom = prenom
        self.date_naissance = date_naissance
        self.email = email
        self.telephone = telephone
        self.id_assureur = id_assureur

    def __repr__(self):
        return "<Assure (%d) %s %s>" % (self.id_assure, self.prenom, self.nom)