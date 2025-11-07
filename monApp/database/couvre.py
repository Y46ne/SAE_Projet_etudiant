from ..app import db

couvre = db.Table('couvre',
	db.Column('id_logement', db.Integer, db.ForeignKey('logement.id_logement'), primary_key=True),
	db.Column('id_assureur', db.Integer, db.ForeignKey('assureur.id_assureur'), primary_key=True),
	db.Column('id_assure', db.Integer, db.ForeignKey('assure.id_assure'), primary_key=True),
	db.Column('date_debut', db.Date, nullable=False)
)