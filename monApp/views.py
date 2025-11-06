from hashlib import sha256
from flask import (
    render_template, request, url_for,
    redirect, flash, jsonify, abort
)
from flask_login import (
    login_user, logout_user,
    login_required, current_user
)
from werkzeug.utils import secure_filename

from .app import app, db, login_manager
from config import *
from monApp.database import (
    User, Assure, Assureur, Logement,
    Piece, Bien, Sinistre, impacte, Justificatif
)
from monApp.forms import *

# ======================================================================
#                           LOGIN MANAGER
# ======================================================================

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# ======================================================================
#                           ROUTES PUBLIQUES
# ======================================================================

@app.route('/')
@app.route('/index/')
def index():
    return render_template("index.html")


@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if not form.is_submitted():
        form.next.data = request.args.get('next')

    elif form.validate_on_submit():
        user = form.get_authenticated_user()
        if user:
            login_user(user)
            flash('Connexion réussie.', 'success')

            next_page = request.args.get('next') or url_for('tableau_de_bord')
            return redirect(next_page)

        else:
            flash('Identifiant ou mot de passe incorrect.', 'danger')

    return render_template('login.html', form=form)


@app.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/creer-compte/', methods=['GET', 'POST'])
def creer_compte():
    form = SignUpForm()

    if form.validate_on_submit():
        try:
            new_user = User(
                Login=form.email.data,
                Password=sha256(form.Password.data.encode()).hexdigest()
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Compte créé avec succès !', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            db.session.rollback()
            flash(f'Erreur : {e}', 'danger')

    return render_template('creeruncompte.html', form=form)


@app.route('/reinitialiser/')
def reinitialiser():
    return render_template('reinitialiser.html')


# ======================================================================
#                           TABLEAU DE BORD
# ======================================================================

@app.route('/tableauDeBord/')
@login_required
def tableau_de_bord():
    return render_template('tableauDeBord.html')


# ======================================================================
#                           GESTION DES LOGEMENTS
# ======================================================================

@app.route('/mes_logements/')
@login_required
def mes_logements():
    logements = current_user.assure_profile.logements if current_user.assure_profile else []
    rows = []

    for l in logements:
        nb_biens = sum(len(p.biens) for p in l.pieces)
        valeur = sum(
            float(b.valeur_actuelle or 0)
            for p in l.pieces for b in p.biens
        )
        rows.append({'logement': l, 'nb_biens': nb_biens, 'valeur': valeur})

    return render_template('mes_logements.html', logements=rows)


@app.route('/ajouter_logement/', methods=['GET', 'POST'])
@login_required
def ajouter_logement():
    form = LogementForm()

    if form.validate_on_submit():
        try:
            logement = Logement(
                adresse=form.adresse.data,
                type_logement=form.type_logement.data,
                surface=form.surface.data,
                description=form.description.data
            )
            logement.assures = form.assures.data

            db.session.add(logement)
            db.session.commit()

            flash("Logement ajouté avec succès", "success")
            return redirect(url_for('mes_logements'))

        except Exception as e:
            db.session.rollback()
            flash(f"Erreur : {e}", "danger")

    return render_template('ajouter_logement.html', form=form)


@app.route('/logement/<int:id>/pieces/')
@login_required
def view_logement_pieces(id):
    logement = Logement.query.get_or_404(id)
    return render_template('logement_pieces.html', logement=logement)


@app.route('/logement/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def update_logement(id):
    logement = Logement.query.get_or_404(id)
    form = LogementForm(obj=logement)

    if form.validate_on_submit():
        try:
            logement.adresse = form.adresse.data
            logement.type_logement = form.type_logement.data
            logement.surface = form.surface.data
            logement.description = form.description.data

            db.session.commit()
            flash("Logement mis à jour", "success")
            return redirect(url_for('mes_logements'))

        except Exception as e:
            db.session.rollback()
            flash(f"Erreur : {e}", "danger")

    return render_template('logement_client.html', form=form)


@app.route('/logement/<int:id>/delete', methods=['GET', 'POST'])
@login_required
def delete_logement(id):
    logement = Logement.query.get_or_404(id)

    try:
        db.session.delete(logement)
        db.session.commit()
        flash('Logement supprimé.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Erreur : {e}', 'danger')

    return redirect(url_for('mes_logements'))


# ======================================================================
#                           GESTION DES PIÈCES
# ======================================================================

@app.route('/ajouter_piece/', methods=['GET', 'POST'])
@login_required
def ajouter_piece():
    form = PieceForm()
    logements = current_user.assure_profile.logements

    form.logement_id.choices = [(l.id_logement, l.adresse) for l in logements]

    if form.validate_on_submit():
        try:
            piece = Piece(
                nom_piece=form.nom_piece.data,
                surface=form.surface.data,
                id_logement=form.logement_id.data
            )
            db.session.add(piece)
            db.session.commit()

            flash("Pièce ajoutée avec succès", "success")
            return redirect(url_for('mes_logements'))

        except Exception as e:
            db.session.rollback()
            flash(f"Erreur : {e}", "danger")

    return render_template('ajouter_piece.html', form=form)


# ======================================================================
#                           GESTION DES BIENS
# ======================================================================

@app.route('/piece/<int:piece_id>/biens/')
@login_required
def gestion_bien(piece_id):
    piece = Piece.query.get_or_404(piece_id)
    biens = Bien.query.filter_by(id_piece=piece.id_piece).all()
    return render_template('gestion_bien.html', piece=piece, biens=biens)


@app.route('/ajouter_bien/', methods=['GET', 'POST'])
@login_required
def ajouter_bien():
    form = AjouterBienForm()
    profil = current_user.assure_profile
    logements = profil.logements
    pieces = [p for log in logements for p in log.pieces]

    form.logement_id.choices = [(l.id_logement, l.adresse) for l in logements]
    form.piece_id.choices = [(p.id_piece, p.nom_piece) for p in pieces]

    if form.validate_on_submit():
        try:
            bien = Bien(
                nom_bien=form.nom_bien.data,
                prix_achat=form.valeur.data,
                categorie=form.categorie.data,
                date_achat=form.date_achat.data,
                etat=form.etat.data,
                id_piece=form.piece_id.data
            )

            db.session.add(bien)
            db.session.flush()

            fichier = form.facture.data
            if fichier:
                filename = secure_filename(fichier.filename)
                user_folder = os.path.join(app.config['UPLOAD_FOLDER'], f"assure_{current_user.id}")
                os.makedirs(user_folder, exist_ok=True)

                file_path = os.path.join(user_folder, f"bien_{bien.id_bien}_{filename}")
                fichier.save(file_path)

                justificatif = Justificatif(
                    chemin_fichier=file_path,
                    type_justificatif="Facture",
                    bien=bien
                )
                db.session.add(justificatif)

            db.session.commit()
            flash("Bien ajouté avec succès", "success")
            return redirect(url_for('mes_logements'))

        except Exception as e:
            db.session.rollback()
            flash(f"Erreur : {e}", "danger")

    return render_template(
        'ajouter_bien.html',
        form=form,
        liste_logement=[{'id': l.id_logement, 'adresse': l.adresse} for l in logements],
        liste_pieces=[{
            'id': p.id_piece,
            'nom_piece': p.nom_piece,
            'id_logement': p.id_logement
        } for p in pieces]
    )


@app.route('/bien/<int:bien_id>/')
@login_required
def voir_bien(bien_id):
    bien = Bien.query.get_or_404(bien_id)
    return render_template('info_bien.html', bien=bien)


# ======================================================================
#                           PARAMÈTRES UTILISATEUR
# ======================================================================

@app.route('/parametres/', methods=['GET', 'POST'])
@login_required
def parametres():
    profil = current_user.assure_profile

    if not profil:
        flash("Profil introuvable.", "danger")
        return redirect(url_for('index'))

    if request.method == 'POST':
        try:
            profil.nom = request.form.get('nom')
            profil.prenom = request.form.get('prenom')
            profil.telephone = request.form.get('telephone')

            db.session.commit()
            flash("Infos mises à jour.", "success")

        except Exception as e:
            db.session.rollback()
            flash(f"Erreur : {e}", "danger")

        return redirect(url_for('parametres'))

    return render_template('parametres.html', profile=profil)


@app.route('/changer_mot_de_passe/', methods=['GET', 'POST'])
@login_required
def changer_mot_de_passe():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        if not current_user.check_password(form.old_password.data):
            flash("Ancien mot de passe incorrect.", "danger")
            return redirect(url_for('changer_mot_de_passe'))

        try:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash("Mot de passe changé.", "success")
            return redirect(url_for('parametres'))

        except Exception as e:
            db.session.rollback()
            flash(f"Erreur : {e}", "danger")

    return render_template('changer_mot_de_passe.html', form=form)


# ======================================================================
#                           SINISTRES
# ======================================================================

@app.route('/declarer_sinistre/', methods=['GET', 'POST'])
@login_required
def declarer_sinistre():
    form = DeclarerSinistre()
    return render_template('declarer_sinistre.html', form=form)


# ======================================================================
#                               MAIN
# ======================================================================

if __name__ == '__main__':
    app.run(debug=True)
