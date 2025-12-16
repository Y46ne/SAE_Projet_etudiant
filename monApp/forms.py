from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, HiddenField, SubmitField, FloatField, SelectField, DateField, TextAreaField, DecimalField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional
from hashlib import sha256 
from .database import *
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from monApp.database.assure import get_tous_les_assures
from flask_wtf.file import FileField, FileAllowed

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
    nom = StringField('Nom', validators=[DataRequired()])
    prenom = StringField('Prénom', validators=[DataRequired()])
    date_naissance = StringField('Date de naissance (YYYY-MM-DD)', validators=[DataRequired()])
    telephone = StringField('Téléphone', validators=[DataRequired()])
    email = StringField('Adresse e-mail', validators=[DataRequired(), Email()])
    Password = PasswordField('Mot de passe', validators=[DataRequired()])
    confirm = PasswordField('Confirmer le mot de passe', validators=[DataRequired(), EqualTo('Password')])
    submit = SubmitField('Créer mon compte')


class ResetPasswordForm(FlaskForm):
    email = StringField('Adresse e-mail', validators=[DataRequired(), Email()])
    new_password = PasswordField('Nouveau mot de passe', validators=[DataRequired()])
    confirm = PasswordField('Confirmer le mot de passe', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Réinitialiser le mot de passe')


class LogementForm(FlaskForm):
    nom_logement = StringField('Nom du logement', validators=[DataRequired()])
    adresse = StringField('Adresse du logement', validators=[DataRequired()])
    type_logement = StringField('Type de logement (Appartement, Maison...)', validators=[DataRequired()])
    surface = FloatField('Surface (m²)', validators=[DataRequired(message="Veuillez renseigner une surface valide.")])
    description = StringField('Description')
    assures = QuerySelectMultipleField(
        'Assures',
        query_factory=get_tous_les_assures,
        get_label="email",
        allow_blank=False            
    )
    submit = SubmitField('Ajouter le logement')


class PieceForm(FlaskForm):
    nom_piece = StringField('Nom de la pièce', validators=[DataRequired()])
    surface = FloatField('Surface (m²)', validators=[DataRequired(message="Veuillez renseigner une surface valide.")])
    logement_id = SelectField('Logement associé', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Ajouter la pièce')


class BienForm(FlaskForm):
    nom_bien = StringField('Nom du bien', validators=[DataRequired()])
    description = TextAreaField('Description')
    categorie = StringField('Catégorie', validators=[DataRequired()])
    date_achat = DateField("Date d'achat", format='%Y-%m-%d', validators=[DataRequired()])
    prix_achat = FloatField("Prix d'achat (€)", validators=[DataRequired()])
    valeur_actuelle = FloatField('Valeur actuelle (€)', render_kw={'readonly': True})
    logement_id = SelectField('Logement associé', coerce=int, validators=[DataRequired()])
    piece_id = SelectField('Pièce associée', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Ajouter le bien')


class SinistreForm(FlaskForm):
    date_sinistre = DateField('Date du sinistre', format='%Y-%m-%d', validators=[DataRequired()])
    type_sinistre = StringField('Type de sinistre (Dégât des eaux, Vol, ...)', validators=[DataRequired()])
    description = TextAreaField('Description détaillée', validators=[DataRequired()])
    numero_sinistre = StringField('Numéro de dossier (si connu)')
    submit = SubmitField('Déclarer le sinistre')


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
    nom_bien = StringField(
        "Nom du bien", 
        validators=[DataRequired(message="Le nom est requis.")]
    )
    prix_achat = FloatField(
        "Prix d'achat (€)",
        validators=[DataRequired(message="Veuillez renseigner un prix valide.")]
    )
    categorie = StringField(
        "Catégorie", 
        validators=[DataRequired(message="La catégorie est requise.")]
    )
    date_achat = DateField(
        "Date d'achat", 
        validators=[DataRequired(message="La date est requise.")]
    )
    logement_id = SelectField(
        "Logement", 
        coerce=int, 
        validators=[DataRequired(message="Le logement est requis.")]
    )
    piece_id = SelectField(
        "Pièce", 
        coerce=int, 
        validators=[DataRequired(message="La pièce est requise.")]
    )
    facture = FileField(
        "Joindre une facture (Facture, Preuve d'achat...)",
        validators=[
            Optional(),
            FileAllowed(['pdf', 'png', 'jpg', 'jpeg'], 'Seuls les images et PDF sont autorisés!')
        ]
    )
    submit = SubmitField("Enregistrer le bien")

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

    biens_selectionnes = QuerySelectMultipleField(
        "Biens sélectionnés",
        query_factory=lambda: Bien.query.all(),
        get_label="nom_bien"
    )

    submit = SubmitField("Générer l'état financier des biens")

class ModifierLogementForm(FlaskForm):
    nom_logement = StringField('Nom du logement', validators=[DataRequired()])
    adresse = StringField('Adresse', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Enregistrer')

class ModifierPieceForm(FlaskForm):
    nom_piece = StringField('Nom de la pièce', validators=[DataRequired()])
    surface = FloatField('Surface (m²)', validators=[DataRequired(message="Veuillez renseigner une surface valide.")])
    submit = SubmitField('Enregistrer')

class ModifierBienForm(FlaskForm):
    nom_bien = StringField('Nom du bien', validators=[DataRequired()])
    categorie = StringField('Catégorie', validators=[DataRequired()])
    date_achat = DateField('Date d\'achat', format='%Y-%m-%d', validators=[Optional()])
    prix_achat = FloatField("Prix d'achat (€)", validators=[DataRequired(message="Veuillez renseigner un prix valide.")])
    valeur_actuelle = FloatField('Valeur actuelle (€)', render_kw={'readonly': True})
    submit = SubmitField('Enregistrer')

class ParametresForm(FlaskForm):
    nom = StringField('Nom', validators=[DataRequired()])
    prenom = StringField('Prénom', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    telephone = StringField('Téléphone', validators=[Optional()])
    submit = SubmitField('Enregistrer')
