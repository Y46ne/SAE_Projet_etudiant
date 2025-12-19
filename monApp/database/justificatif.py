from ..app import db
from datetime import datetime
import os
from flask import current_app


class Justificatif(db.Model):
    __tablename__ = 'justificatif'
    id_justificatif = db.Column(db.Integer, primary_key=True)
    type_justificatif = db.Column(db.String(50))
    chemin_fichier = db.Column(db.String(255), nullable=False)
    date_ajout = db.Column(db.DateTime, nullable=False)
    id_bien = db.Column(db.Integer, db.ForeignKey('bien.id_bien'), unique=True, nullable=False)
    
    bien = db.relationship('Bien', backref=db.backref('justificatif', uselist=False))

    def __init__(self, chemin_fichier, type_justificatif=None, date_ajout=None, id_bien=None):
        self.type_justificatif = type_justificatif
        self.chemin_fichier = chemin_fichier
        self.date_ajout = date_ajout or datetime.utcnow()
        self.id_bien = id_bien

    def __repr__(self):
        return f"<Justificatif {self.id_justificatif} {self.type_justificatif}>"

    @property
    def is_image(self):
        if not self.chemin_fichier:
            return False
        return self.chemin_fichier.lower().endswith(('.png', '.jpg', '.jpeg'))

    @property
    def is_pdf(self):
        if not self.chemin_fichier:
            return False
        return self.chemin_fichier.lower().endswith('.pdf')

    @property
    def fichier_existe(self):
        if not self.chemin_fichier:
            return False
        try:
            return os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], self.chemin_fichier))
        except:
            return False