from ..app import db

justifie = db.Table('justifie',
	db.Column('id_logement', db.Integer, db.ForeignKey('logement.id_logement'), primary_key=True),
	db.Column('id_justificatif', db.Integer, db.ForeignKey('justificatif.id_justificatif'), primary_key=True)
)