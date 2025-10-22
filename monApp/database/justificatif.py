from ..app import db

class Justificatif(db.Model):
    id_justificatif = db.Column(db.Integer, primary_key=True)
    type_justificatif = db.Column(db.String(100))
    chemin_fichier = db.Column(db.String(255))
    date_ajout = db.Column(db.String(100))
    id_bien = db.Column(db.Integer, db.ForeignKey('bien.id_bien'), nullable=False)

    def __init__(self, type_justificatif, chemin_fichier, date_ajout, id_bien):
        self.type_justificatif = type_justificatif
        self.chemin_fichier = chemin_fichier
        self.date_ajout = date_ajout
        self.id_bien = id_bien

    def __repr__(self):
        return "<Justificatif (%d) %s>" % (self.id_justificatif, self.type_justificatif)