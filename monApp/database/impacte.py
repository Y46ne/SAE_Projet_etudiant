from ..app import db

impacte = db.Table('impacte',
	db.Column('id_sinistre', db.Integer, db.ForeignKey('sinistre.id_sinistre'), primary_key=True),
	db.Column('id_bien', db.Integer, db.ForeignKey('bien.id_bien'), primary_key=True),
	db.Column('degat_estime', db.Numeric(10,2))
)