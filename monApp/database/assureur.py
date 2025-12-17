from ..app import db
from monApp.database.couvre import couvre

class Assureur(db.Model):
    __tablename__ = 'assureur'
    id_assureur = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100), db.ForeignKey('user.Login'), unique=True, nullable=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    telephone = db.Column(db.String(20))
    mot_de_passe = db.Column(db.String(255), nullable=False)
    societe = db.Column(db.String(100))
    logements_couverts = db.relationship('Logement', secondary=couvre, back_populates='assureurs', lazy='subquery')

    def __init__(self, nom, prenom, email, mot_de_passe, telephone=None, societe=None):
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.mot_de_passe = mot_de_passe
        self.telephone = telephone
        self.societe = societe
        self.login = email

    def __repr__(self):
        return f"<Assureur {self.id_assureur} {self.prenom} {self.nom}>"