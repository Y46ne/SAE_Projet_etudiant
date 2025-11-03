from ..app import db

possede = db.Table('possede',
	db.Column('id_assure', db.Integer, db.ForeignKey('assure.id_assure'), primary_key=True),
	db.Column('id_logement', db.Integer, db.ForeignKey('logement.id_logement'), primary_key=True)
)

couvre = db.Table('couvre',
	db.Column('id_logement', db.Integer, db.ForeignKey('logement.id_logement'), primary_key=True),
	db.Column('id_assureur', db.Integer, db.ForeignKey('assureur.id_assureur'), primary_key=True),
	db.Column('id_assure', db.Integer, db.ForeignKey('assure.id_assure'), primary_key=True),
	db.Column('date_debut', db.Date, nullable=False)
)

justifie = db.Table('justifie',
	db.Column('id_logement', db.Integer, db.ForeignKey('logement.id_logement'), primary_key=True),
	db.Column('id_justificatif', db.Integer, db.ForeignKey('justificatif.id_justificatif'), primary_key=True)
)

impacte = db.Table('impacte',
	db.Column('id_sinistre', db.Integer, db.ForeignKey('sinistre.id_sinistre'), primary_key=True),
	db.Column('id_bien', db.Integer, db.ForeignKey('bien.id_bien'), primary_key=True),
	db.Column('degat_estime', db.Numeric(10,2))
)

__all__ = ['possede', 'couvre', 'justifie', 'impacte']
