from ..app import db

possede = db.Table('possede',
	db.Column('id_assure', db.Integer, db.ForeignKey('assure.id_assure'), primary_key=True),
	db.Column('id_logement', db.Integer, db.ForeignKey('logement.id_logement'), primary_key=True)
)