from ..app import db

class Assureur(db.Model):
    id_assureur = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100))
    prenom = db.Column(db.String(100))
    email = db.Column(db.String(100), db.ForeignKey('user.Login'), unique=True)
    telephone = db.Column(db.String(20))
    societe = db.Column(db.String(100))

    def __init__(self, nom, prenom, email, telephone, societe):
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.telephone = telephone
        self.societe = societe

    def __repr__(self):
        return "<Assureur (%d) %s %s>" % (self.id_assureur, self.prenom, self.nom)