from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, HiddenField, SubmitField, FloatField, SelectField, DateField, TextAreaField, DecimalField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, ValidationError, Regexp
from hashlib import sha256 
from .database import *
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from monApp.database.assure import get_tous_les_assures
from flask_wtf.file import FileField, FileAllowed
from datetime import datetime, timedelta

# --- Fonctions de validation réutilisables (Refactoring) ---

def check_name_format(valeur, field_name="Ce champ", min_segment=2):
    """Valide le format d'un nom ou prénom (lettres, tirets, longueur)."""
    valeur = valeur.strip()
    for char in valeur:
        if not (char.isalpha() or char in " -"):
            raise ValidationError(f"{field_name} ne doit contenir que des lettres.")
    
    if valeur.startswith('-') or valeur.endswith('-'):
        raise ValidationError(f"{field_name} ne peut pas commencer ou finir par un tiret.")

    segments = valeur.split('-')
    for s in segments:
        if len(s.strip()) < min_segment:
            raise ValidationError(f"Chaque partie de {field_name} doit avoir au moins {min_segment} lettres.")

def check_address_format(valeur, min_len=10):
    """Valide le format d'une adresse."""
    valeur = valeur.strip()
    if len(valeur) < min_len:
        raise ValidationError("L'adresse semble trop courte.")

    derniers_est_espace = False
    for char in valeur:
        if not (char.isalnum() or char in " -,'"):
            raise ValidationError(f"Le caractère '{char}' n'est pas autorisé dans une adresse.")
        if char == " " and derniers_est_espace:
            raise ValidationError("L'adresse contient trop d'espaces consécutifs.")
        derniers_est_espace = (char == " ")

    if not any(char.isdigit() for char in valeur):
        raise ValidationError("L'adresse doit inclure un numéro.")
    if not any(char.isalpha() for char in valeur):
        raise ValidationError("L'adresse doit inclure un nom de rue.")

    if valeur[0] in "-,' " or valeur[-1] in "-,' ":
        raise ValidationError("L'adresse ne peut pas commencer ou finir par un symbole ou un espace.")

def check_simple_text(valeur, field_name="Ce champ", min_len=2, allowed_chars=" -'"):
    """Valide un texte simple (nom de bien, pièce, logement)."""
    valeur = valeur.strip()
    if len(valeur) < min_len:
        raise ValidationError(f"{field_name} est trop court ({min_len} min).")
    if not any(char.isalpha() for char in valeur):
        raise ValidationError(f"{field_name} doit contenir au moins une lettre.")
    for char in valeur:
        if not (char.isalnum() or char in allowed_chars):
            raise ValidationError(f"Caractère interdit : '{char}'.")

class LoginForm(FlaskForm):
    Login = StringField('Identifiant', validators=[DataRequired()])
    Password = PasswordField('Mot de passe', validators=[DataRequired()])
    next = HiddenField()

    def get_authenticated_user(self):
        unUser = User.query.get(self.Login.data)

        if unUser is None:
            return None

        m = sha256()
        m.update(self.Password.data.encode())
        passwd_input_hache = m.hexdigest()
        print(passwd_input_hache)

        if passwd_input_hache == unUser.Password:
            return unUser 
        return None

class SignUpForm(FlaskForm):
    nom = StringField('Nom', validators=[DataRequired(message="Le nom est requis.")])
    prenom = StringField('Prénom', validators=[DataRequired(message="Le prénom est requis.")])
    date_naissance = DateField(
        'Date de naissance', 
        format='%Y-%m-%d',
        validators=[Optional()]
    )
    telephone = StringField(
        'Téléphone', 
        validators=[
            DataRequired(message="Le téléphone est requis."),
            Regexp(r'^\d{10}$', message="Le numéro doit contenir exactement 10 chiffres (ex: 0612345678).")
        ]
    )
    email = StringField(
        'Adresse e-mail', 
        validators=[
            DataRequired(message="L'email est requis."), 
            Email(message="Adresse email invalide.")
        ]
    )
    Password = PasswordField(
        'Mot de passe', 
        validators=[
            DataRequired(message="Le mot de passe est requis."),
            Length(min=8, message="Le mot de passe doit faire au moins 8 caractères.")
        ]
    )
    confirm = PasswordField('Confirmer le mot de passe', validators=[
        DataRequired(), 
        EqualTo('Password', message="Les mots de passe ne correspondent pas.")
    ])
    submit = SubmitField('Créer mon compte')

    def validate_nom(self, field):
        check_name_format(field.data, "Le nom", 2)

    def validate_prenom(self, field):
        check_name_format(field.data, "Le prénom", 3)

    def validate_date_naissance(self, field): 
        date_obj = field.data
        if date_obj is None: return
        today = datetime.now().date()
        age_minimum = 18
        if (today.year - date_obj.year - ((today.month, today.day) < (date_obj.month, date_obj.day))) < age_minimum:
            raise ValidationError(f"Vous devez avoir au moins {age_minimum} ans pour vous inscrire.")



class ResetPasswordForm(FlaskForm):
    email = StringField('Adresse e-mail', validators=[DataRequired(), Email()])
    new_password = PasswordField('Nouveau mot de passe', validators=[DataRequired()])
    confirm = PasswordField('Confirmer le mot de passe', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Réinitialiser le mot de passe')


class LogementForm(FlaskForm):
    nom_logement = StringField('Nom du logement', validators=[DataRequired()])
    adresse = StringField('Adresse du logement', validators=[DataRequired()])
    type_logement = SelectField(
        'Type de logement', 
        choices=[
            ('', 'Sélectionner un type'), 
            ('Maison', 'Maison'), 
            ('Appartement', 'Appartement'), 
            ('Studio', 'Studio'), 
            ('Autre', 'Autre')
        ],
        validators=[DataRequired(message="Veuillez choisir un type de logement.")]
    )
    surface = FloatField('Surface (m²)', validators=[DataRequired(message="Veuillez renseigner une surface valide.")])
    description = StringField('Description')
    assures = QuerySelectMultipleField(
        'Assures',
        query_factory=get_tous_les_assures,
        get_label="email",
        allow_blank=True
    )
    submit = SubmitField('Ajouter le logement')

    def validate_nom_logement(self, field):
        check_simple_text(field.data, "Le nom du logement", 3)

    def validate_adresse(self, field):
        check_address_format(field.data, min_len=7)

    def validate_surface(self, field):
        if field.data <= 0:
            raise ValidationError("La surface doit être un nombre positif.")
        if field.data > 10000:
            raise ValidationError("Surface incohérente.")


class PieceForm(FlaskForm):
    nom_piece = StringField('Nom de la pièce', validators=[DataRequired()])
    surface = FloatField('Surface (m²)', validators=[DataRequired(message="Veuillez renseigner une surface valide.")])
    logement_id = SelectField('Logement associé', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Ajouter la pièce')

    def validate_nom_piece(self, field):
        check_simple_text(field.data, "Le nom de la pièce", 2, " -")

    def validate_surface(self, field):
        if field.data <= 0:
            raise ValidationError("La surface doit être positive.")
        if field.data > 1000:
            raise ValidationError("La surface semble incohérente pour une seule pièce.")


class DeleteForm(FlaskForm):
    submit = SubmitField('Supprimer')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(
        'Ancien mot de passe', 
        validators=[DataRequired(message="Champ requis.")]
    )
    
    new_password = PasswordField(
        'Nouveau mot de passe', 
        validators=[
            DataRequired(message="Champ requis."),
            Length(min=8, message="Le mot de passe doit faire au moins 8 caractères.")
        ]
    )
    
    confirm_password = PasswordField(
        'Confirmer le nouveau mot de passe', 
        validators=[
            DataRequired(message="Champ requis."),
            EqualTo('new_password', message='Les mots de passe ne correspondent pas.')
        ]
    )
    
    submit = SubmitField('Changer le mot de passe')

class AjouterBienForm(FlaskForm):
    nom_bien = StringField("Nom du bien", validators=[DataRequired(message="Le nom est requis.")])
    prix_achat = FloatField("Prix d'achat (€)",validators=[DataRequired(message="Veuillez renseigner un prix valide.")])
    categorie = SelectField(
        "Catégorie", 
        choices=[
            ('', 'Sélectionner une catégorie'),
            ('Electromenager', 'Électroménager'),
            ('Mobilier', 'Mobilier'),
            ('Multimedia', 'Multimédia'),
            ('Vetements', 'Vêtements'),
            ('Bijoux', 'Bijoux'),
            ('Loisirs', 'Loisirs'),
            ('Vaisselle', 'Vaisselle'),
            ('Outillage', 'Outillage'),
            ('Autre', 'Autre')
        ],
        validators=[DataRequired(message="La catégorie est requise.")]
    )
    date_achat = DateField("Date d'achat", validators=[DataRequired(message="La date est requise.")])
    logement_id = SelectField("Logement", coerce=int, validators=[DataRequired(message="Le logement est requis.")])
    piece_id = SelectField("Pièce", coerce=int, validators=[DataRequired(message="La pièce est requise.")])
    facture = FileField(
        "Joindre une facture (Facture, Preuve d'achat...)",
        validators=[Optional(),FileAllowed(['pdf', 'png', 'jpg', 'jpeg'], 'Seuls les images et PDF sont autorisés!')]
    )
    submit = SubmitField("Enregistrer le bien")

    def validate_nom_bien(self, field):
        check_simple_text(field.data, "Le nom du bien", 1)

    def validate_date_achat(self, field):
        if field.data:
            today = datetime.now().date()
            if field.data > today:
                raise ValidationError("La date d'achat ne peut pas être dans le futur.")
            
            if field.data.year < 0:
                raise ValidationError("La date d'achat semble incorrecte (trop ancienne).")

    def validate_prix_achat(self, field):
        if field.data is not None and field.data < 0:
            raise ValidationError("Le prix d'achat ne peut pas être négatif.")



class DeclarerSinistre(FlaskForm):
    date_sinistre = DateField(
        "Date du sinistre",
        format="%Y-%m-%d",
        validators=[DataRequired(message="Veuillez entrer une date valide.")]
    )

    type_sinistre = SelectField(
        "Type de sinistre",
        choices=[
            ("incendie", "Incendie"),
            ("degat_eau", "Dégât des eaux"),
            ("vol", "Vol"),
            ("tempete", "Tempête"),
            ("bris_glace", "Bris de glace"),
        ],
        validators=[DataRequired(message="Veuillez sélectionner un type de sinistre.")]
    )

    description = TextAreaField(
        "Description",
        validators=[Optional()]
    )

    biens_selectionnes = QuerySelectMultipleField(
        "Biens sélectionnés",
        query_factory=lambda: Bien.query.all(),
        get_label="nom_bien"
    )

    submit = SubmitField("Générer l'état financier des biens")

    def validate_date_sinistre(self, field):
        if field.data:
            today = datetime.now().date()
            
            if field.data > today:
                raise ValidationError("La date du sinistre ne peut pas être dans le futur.")
            
            un_an_passe = today - timedelta(days=365)
            if field.data < un_an_passe:
                raise ValidationError("Vous ne pouvez pas déclarer un sinistre vieux de plus d'un an.")

class ModifierLogementForm(FlaskForm):
    nom_logement = StringField('Nom du logement', validators=[DataRequired()])
    adresse = StringField('Adresse', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Enregistrer')

    def validate_nom_logement(self, field):
        check_simple_text(field.data, "Le nom du logement", 3)

    def validate_adresse(self, field):
        check_address_format(field.data, min_len=10)

class ModifierPieceForm(FlaskForm):
    nom_piece = StringField('Nom de la pièce', validators=[DataRequired()])
    surface = FloatField('Surface (m²)', validators=[DataRequired(message="Veuillez renseigner une surface valide.")])
    submit = SubmitField('Enregistrer')

    def validate_nom_piece(self, field):
        check_simple_text(field.data, "Le nom de la pièce", 2, " -")

    def validate_surface(self, field):
        if field.data <= 0:
            raise ValidationError("La surface doit être positive.")
        if field.data > 1000:
            raise ValidationError("La surface semble incohérente.")

class ModifierBienForm(FlaskForm):
    nom_bien = StringField(
        "Nom du bien", 
        validators=[DataRequired(message="Le nom est requis.")]
    )
    
    categorie = SelectField(
        "Catégorie", 
        choices=[
            ('', 'Sélectionner une catégorie'),
            ('Electromenager', 'Électroménager'),
            ('Mobilier', 'Mobilier'),
            ('Multimedia', 'Multimédia'),
            ('Vetements', 'Vêtements'),
            ('Bijoux', 'Bijoux'),
            ('Loisirs', 'Loisirs'),
            ('Vaisselle', 'Vaisselle'),
            ('Outillage', 'Outillage'),
            ('Autre', 'Autre')
        ],
        validators=[DataRequired(message="La catégorie est requise.")]
    )
    
    date_achat = DateField(
        "Date d'achat", 
        format='%Y-%m-%d', 
        validators=[DataRequired(message="La date est requise.")]
    )
    
    prix_achat = FloatField(
        "Prix d'achat (€)", 
        validators=[DataRequired(message="Veuillez renseigner un prix valide.")]
    )
    
    valeur_actuelle = FloatField('Valeur actuelle (€)', render_kw={'readonly': True})
    
    submit = SubmitField('Enregistrer')

    def validate_nom_bien(self, field):
        check_simple_text(field.data, "Le nom du bien", 1)

    def validate_date_achat(self, field):
        if field.data:
            today = datetime.now().date()
            if field.data > today:
                raise ValidationError("La date d'achat ne peut pas être dans le futur.")
            
            if field.data.year < 0:
                raise ValidationError("La date d'achat semble incorrecte (trop ancienne).")

    def validate_prix_achat(self, field):
        if field.data is not None and field.data < 0:
            raise ValidationError("Le prix d'achat ne peut pas être négatif.")
        


class ParametresForm(FlaskForm):
    nom = StringField(
        'Nom', 
        validators=[DataRequired(message="Le nom est requis.")]
    )
    
    prenom = StringField(
        'Prénom', 
        validators=[DataRequired(message="Le prénom est requis.")]
    )
    
    email = StringField(
        'Email', 
        validators=[DataRequired(), Email()] 
    )
    
    telephone = StringField(
        'Téléphone', 
        validators=[
            DataRequired(message="Le téléphone est requis."),
            Regexp(r'^\d{10}$', message="Le numéro doit contenir exactement 10 chiffres (ex: 0612345678).")
        ]
    )
    
    submit = SubmitField('Enregistrer')

    def validate_nom(self, field):
        valeur = field.data.strip()
        for char in valeur:
            if not (char.isalpha() or char in " -"):
                raise ValidationError("Le nom ne doit contenir que des lettres.")
        
        if valeur.startswith('-') or valeur.endswith('-'):
            raise ValidationError("Le nom ne peut pas commencer ou finir par un tiret.")

        segments = valeur.split('-')
        for s in segments:
            nettoyé = s.strip()
            if len(nettoyé) < 2:
                raise ValidationError("Chaque partie du nom doit avoir au moins 2 lettres.")

    def validate_prenom(self, field):
        valeur = field.data.strip()
        for char in valeur:
            if not (char.isalpha() or char in " -"):
                raise ValidationError("Le prénom ne doit contenir que des lettres.")
        
        if valeur.startswith('-') or valeur.endswith('-'):
            raise ValidationError("Le prénom ne peut pas commencer ou finir par un tiret.")

        segments = valeur.split('-')
        for s in segments:
            nettoyé = s.strip()
            if len(nettoyé) < 3:
                raise ValidationError("Chaque partie du prénom doit avoir au moins 3 lettres.")


class UpdateSinistreForm(FlaskForm):
    statut = SelectField(
        'Statut du sinistre',
        choices=[
            ('Déclaré', 'Déclaré'),
            ('En cours d\'expertise', 'En cours d\'expertise'),
            ('Expertisé', 'Expertisé'),
            ('Clos', 'Clos')
        ],
        validators=[DataRequired()]
    )
    montant_estime = DecimalField('Montant estimé', validators=[Optional()])
    montant_final = DecimalField('Montant final', validators=[Optional()])
    submit = SubmitField('Mettre à jour le sinistre')


class ModifierAssureForm(FlaskForm):
    nom = StringField('Nom', validators=[DataRequired(message="Le nom est requis.")])
    prenom = StringField('Prénom', validators=[DataRequired(message="Le prénom est requis.")])
    date_naissance = DateField(
        'Date de naissance', 
        format='%Y-%m-%d',
        validators=[Optional()]
    )
    telephone = StringField(
        'Téléphone', 
        validators=[
            DataRequired(message="Le téléphone est requis."),
            Regexp(r'^\d{10}$', message="Le numéro doit contenir exactement 10 chiffres.")
        ]
    )
    email = StringField('Adresse e-mail', validators=[DataRequired(), Email()])
    submit = SubmitField('Enregistrer les modifications')

    def validate_nom(self, field):
        valeur = field.data.strip()
        for char in valeur:
            if not (char.isalpha() or char in " -"):
                raise ValidationError("Le nom ne doit contenir que des lettres.")

        segments = valeur.split('-')
        for s in segments:
            nettoyé = s.strip()
            if len(nettoyé) < 2:
                raise ValidationError("Chaque partie du nom doit avoir au moins 2 lettres.")
        
        if valeur.startswith('-') or valeur.endswith('-'):
            raise ValidationError("Le nom ne peut pas commencer ou finir par un tiret.")

    def validate_prenom(self, field):
        valeur = field.data.strip()
        for char in valeur:
            if not (char.isalpha() or char in " -"):
                raise ValidationError("Le prénom ne doit contenir que des lettres.")

        segments = valeur.split('-')
        for s in segments:
            nettoyé = s.strip()
            if len(nettoyé) < 3:
                raise ValidationError("Chaque partie du prénom doit avoir au moins 3 lettres.")

        if valeur.startswith('-') or valeur.endswith('-'):
            raise ValidationError("Le prénom ne peut pas commencer ou finir par un tiret.")

    def validate_date_naissance(self, field): 
        date_obj = field.data 
        if not date_obj:
            return

        if date_obj.year < 1900: 
            raise ValidationError("Date de naissance invalide. (Incohérente)") 
        
        today = datetime.now().date()
        if date_obj > today: 
            raise ValidationError("La date de naissance ne peut pas être dans le futur.") 
        
        age_minimum = 18
        if (today.year - date_obj.year - ((today.month, today.day) < (date_obj.month, date_obj.day))) < age_minimum:
            raise ValidationError(f"Vous devez avoir au moins {age_minimum} ans.")