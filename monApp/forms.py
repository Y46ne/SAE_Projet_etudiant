from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, HiddenField, SubmitField, FloatField, SelectField, DateField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo
from hashlib import sha256 
from .database import User
from .app import db 
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from monApp.database.assure import get_tous_les_assures

class LoginForm(FlaskForm):
    Login = StringField('Identifiant', validators=[DataRequired()])
    Password = PasswordField('Mot de passe', validators=[DataRequired()])
    next = HiddenField()

    def get_authenticated_user(self):
        user = db.session.get(User, self.Login.data)
        if not user:
            return None
        m = sha256()
        m.update(self.Password.data.encode())
        hashed = m.hexdigest()
        return user if user.Password == hashed else None


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
    adresse = StringField('Adresse du logement', validators=[DataRequired()])
    type_logement = StringField('Type de logement (Appartement, Maison...)', validators=[DataRequired()])
    surface = FloatField('Surface (m²)', validators=[DataRequired()])
    description = StringField('Description')
    assures = QuerySelectMultipleField(
        'Assures',
        query_factory=get_tous_les_assures,
        get_label='nom',            
        allow_blank=False            
    )
    submit = SubmitField('Ajouter le logement')


class PieceForm(FlaskForm):
    nom_piece = StringField('Nom de la pièce', validators=[DataRequired()])
    surface = FloatField('Surface (m²)', validators=[DataRequired()])
    type_piece = StringField('Type de pièce (Salon, Chambre, Cuisine...)', validators=[DataRequired()])
    etage = StringField('Étage (ex: RDC, 1er, Sous-sol)', validators=[DataRequired()]) # Added etage field
    logement_id = SelectField('Logement associé', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Ajouter la pièce')


class BienForm(FlaskForm):
    nom_bien = StringField('Nom du bien', validators=[DataRequired()])
    description = TextAreaField('Description')
    categorie = StringField('Catégorie', validators=[DataRequired()])
    date_achat = DateField("Date d'achat", format='%Y-%m-%d', validators=[DataRequired()])
    prix_achat = FloatField("Prix d'achat (€)", validators=[DataRequired()])
    etat = StringField('État (Neuf, Bon, Usé...)', validators=[DataRequired()])
    valeur_actuelle = FloatField('Valeur actuelle (€)', validators=[DataRequired()])
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
