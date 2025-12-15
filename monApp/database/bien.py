from ..app import db
from monApp.database.impacte import impacte


class Bien(db.Model):
    __tablename__ = 'bien'
    id_bien = db.Column(db.Integer, primary_key=True)
    nom_bien = db.Column(db.String(255), nullable=False)
    categorie = db.Column(db.String(100))
    date_achat = db.Column(db.Date)
    prix_achat = db.Column(db.Float)
    valeur_actuelle = db.Column(db.Float)

    id_piece = db.Column(db.Integer, db.ForeignKey('piece.id_piece'), nullable=False)
    sinistres = db.relationship('Sinistre', secondary=impacte, lazy='subquery', backref=db.backref('biens', lazy='subquery'))

    def __init__(self, nom_bien, id_piece, description=None, categorie=None, date_achat=None, prix_achat=None, id_justificatif=None):
        self.nom_bien = nom_bien
        self.description = description
        self.categorie = categorie
        self.date_achat = date_achat
        self.prix_achat = prix_achat
        self.id_piece = id_piece
        self.id_justificatif = id_justificatif
        self.valeur_actuelle = self.calculer_valeur_actuelle()
    def calculer_valeur_actuelle(self):
        """
        Calcule la valeur actuelle du bien en fonction de la date d'achat, de la catégorie et du prix d'achat.
        Dépréciation annuelle selon la catégorie :
        - Electromenager : 20%
        - Mobilier : 10%
        - Multimedia : 25%
        - Vetements : 30%
        - Bijoux : 5%
        - Loisirs : 15%
        - Vaisselle : 10%
        - Outillage : 12%
        - Autre : 8%
        """
        import datetime
        if not self.date_achat or not self.prix_achat:
            return None
        taux_categories = {
            "electromenager": 0.15,   
            "multimedia": 0.25,       
            "mobilier": 0.10,         
            "vetements": 0.30,        
            "bijoux": 0.05,           
            "loisirs": 0.10,         
            "vaisselle": 0.10,        
            "outillage": 0.15,        
            "autre": 0.10  
        }
        taux = 0.08 
        if self.categorie:
            cat = self.categorie.strip().lower()
            taux = taux_categories.get(cat, 0.08)
        annees = (datetime.date.today() - self.date_achat).days / 365.25
        prix = float(self.prix_achat)
        valeur = prix * ((1 - taux) ** annees)
        return max(valeur, 0)

    def __repr__(self):
        return "<Bien (%d) %s>" % (self.id_bien, self.nom_bien)