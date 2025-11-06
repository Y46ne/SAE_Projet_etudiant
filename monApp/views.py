from .app import app, db, login_manager
from config import *
from flask import render_template, request, url_for, redirect, flash, jsonify
from monApp.database import User, Assure, Assureur, Logement, Piece, Bien, Sinistre, impacte
from monApp.forms import *
from flask_login import login_user, logout_user, login_required, current_user
from hashlib import sha256
from flask import abort

@app.route('/')
@app.route('/index/')
def index():
    if len(request.args) == 0:
        return render_template("index.html")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    unForm = LoginForm()
    user=None
    if not unForm.is_submitted():
        unForm.next.data = request.args.get('next')
    elif unForm.validate_on_submit():
        user = unForm.get_authenticated_user()
        if user:
            login_user(user)
            flash('Connexion réussie.', 'success')
            next_page = request.args.get('next') or url_for('tableau_de_bord')
            return redirect(next_page)
        else:
            flash('Identifiant ou mot de passe incorrect.', 'danger')
    return render_template('login.html', form=unForm)

@app.route ("/logout/")
def logout():
    logout_user()
    return redirect ( url_for ('login'))

@app.route('/info_bien/')
def info_bien(id):
    bien = Bien.query.get_or_404(id)
    return render_template('info_bien.html', bien=bien)


@app.route('/reinitialiser/')
def reinitialiser():
    return render_template('reinitialiser.html')


@app.route('/tableauDeBord/')
def tableau_de_bord():
    return render_template('tableauDeBord.html')

@app.route('/modifier_bien/')
def modifier_bien():
    return render_template('modifier_bien.html')

@app.route('/modifier_pièce/')
def modifier_piece():
    return render_template('modifier_pièce.html')

@app.route('/supprimer_pièce/')
def supprimer_piece():
    return render_template('supprimer_pièce.html')

@app.route('/declarer_sinstre')
def declarer_sinistre():
    form = DeclarerSinistre()
    return render_template('declarer_sinistre.html', form=form)


@app.route('/ajouter_logement/', methods=['GET', 'POST'])
def ajouter_logement():
    form = LogementForm()
    if form.validate_on_submit():

        liste_objets_assures = form.assures.data

        insertedLogement = Logement(
            adresse=form.adresse.data,
            type_logement=form.type_logement.data,
            surface=form.surface.data, 
            description=form.description.data
        )

        insertedLogement.assures = liste_objets_assures

        db.session.add(insertedLogement)
        db.session.commit()
        
        print("-------------------------logement ajoute----------------------")

        return redirect(url_for('mes_logements'))

    print("-------------------------probleme----------------------")
    return render_template('ajouter_logement.html', form=form)

@app.route('/gestion_bien/')
def gestion_bien():
    form = LogementForm()
    return render_template('gestion_bien.html',form=form)
    

@app.route('/mes_logements/')
def mes_logements():
    logements = []
    if current_user.assure_profile:
        logements = current_user.assure_profile.logements

    rows = []

    for l in logements:
        nb_biens = 0
        valeur = 0.0
        for p in l.pieces:
            nb_biens += len(getattr(p, 'biens', []))
            for b in getattr(p, 'biens', []):
                try:
                    if b.valeur_actuelle is not None:
                        valeur += float(b.valeur_actuelle)
                except Exception:
                    pass
        rows.append({'logement': l, 'nb_biens': nb_biens, 'valeur': valeur})
    return render_template('mes_logements.html', logements=rows)


@app.route('/logement/<int:id>/pieces/')
def view_logement_pieces(id):
    logement = Logement.query.get_or_404(id)
    return render_template('logement_pieces.html', logement=logement)


@app.route('/logement/<int:id>/delete', methods=['GET', 'POST'])
def delete_logement(id):
    logement = Logement.query.get_or_404(id)
    try:
        db.session.delete(logement)
        db.session.commit()
        flash('Logement supprimé.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression : {e}', 'danger')
    return redirect(url_for('mes_logements'))


@app.route('/logement/<int:id>/edit', methods=['GET', 'POST'])
def update_logement(id):
    logement = Logement.query.get_or_404(id)
    form = LogementForm(obj=logement)
    if form.validate_on_submit():
        logement.adresse = form.adresse.data
        logement.type_logement = form.type_logement.data
        logement.surface = form.surface.data
        logement.description = form.description.data
        try:
            db.session.commit()
            flash('Logement mis à jour.', 'success')
            return redirect(url_for('mes_logements'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la mise à jour : {e}', 'danger')
    return render_template('logement_client.html', form=form)




@app.route('/creer-compte/', methods=['GET', 'POST'])
def creer_compte():
    form = SignUpForm()
    if form.validate_on_submit():
        try:
            # Le modèle User n'attend que Login et Password
            new_user = User(
                Login=form.email.data,
                Password=sha256(form.Password.data.encode()).hexdigest()
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Votre compte a été créé avec succès ! Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la création du compte : {e}', 'danger')
    return render_template('creeruncompte.html', form=form)
    
@app.route('/TableauDeBord/')
def TableauDeBord():
    return render_template('TableauDeBord.html')

@app.route('/parametres/', methods=['GET', 'POST'])
def parametres():
    """
    Affiche la page des paramètres et gère la mise à jour
    des informations du profil (nom, prenom, telephone).
    """
    # Récupère le bon profil (Assure ou Assureur)
    # Note: 'assure' et 'assureur' sont les noms des relations
    # définies dans ton modèle User.
    profile = current_user.assure_profile
    
    if profile is None:
        flash("Erreur : Profil utilisateur introuvable.", "danger")
        return redirect(url_for('index'))

    if request.method == 'POST':
        # C'est une soumission de formulaire pour ENREGISTRER
        try:
            profile.nom = request.form.get('nom')
            profile.prenom = request.form.get('prenom')
            profile.telephone = request.form.get('telephone')
            
            db.session.commit()
            flash('Vos informations ont été mises à jour avec succès.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la mise à jour : {e}', 'danger')
        
        # Redirige vers la même page pour voir les changements
        return redirect(url_for('parametres'))

    # Si c'est un GET, on affiche simplement la page
    return render_template('parametres.html', profile=profile)


@app.route('/changer_mot_de_passe/', methods=['GET', 'POST'])
def changer_mot_de_passe():
    """
    Affiche et traite le formulaire de changement de mot de passe.
    """
    form = ChangePasswordForm()
    if form.validate_on_submit():
        # 1. Vérifier l'ancien mot de passe
        if not current_user.check_password(form.old_password.data):
            flash("L'ancien mot de passe est incorrect.", "danger")
            return redirect(url_for('changer_mot_de_passe'))
        
        # 2. Mettre à jour avec le nouveau mot de passe
        try:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Votre mot de passe a été changé avec succès.', 'success')
            return redirect(url_for('parametres')) # Retourne aux paramètres
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors du changement de mot de passe : {e}', 'danger')
    return render_template('changer_mot_de_passe.html', form=form)

@app.route('/ajouter_piece/', methods=['GET', 'POST'])
def ajouter_piece():
    form = PieceForm()
    return render_template('ajouter_piece.html', form=form)

@app.route('/ajouter_bien/', methods=['GET', 'POST'])
def ajouter_bien():

    form = AjouterBienForm()
    """
    # 2. Récupère les logements de l'utilisateur pour le menu déroulant
    assure_profil = current_user.assure
    user_logements = assure_profil.logements # (Suppose que la relation s'appelle 'logements')
    
    # 3. Prépare la liste de TOUTES les pièces de l'utilisateur pour le JS
    #    (Le JS s'occupera de filtrer)
    user_pieces = []
    for log in user_logements:
        user_pieces.extend(log.pieces) # (Suppose que la relation s'appelle 'pieces')

    # 4. On passe les choix aux menus déroulants du formulaire
    #    (Note: le template HTML manuel les utilise aussi)
    form.logement_id.choices = [(l.id_logement, l.adresse) for l in user_logements]
    form.piece_id.choices = [(p.id_piece, p.nom_piece) for p in user_pieces]

    if form.validate_on_submit():
        try:
            # 5. Récupère les données du formulaire
            nouveau_bien = Bien(
                nom_bien=form.nom_bien.data,
                prix_achat=form.valeur.data, # Note: ton modèle utilise prix_achat
                categorie=form.categorie.data,
                date_achat=form.date_achat.data,
                etat=form.etat.data,
                id_piece=form.piece_id.data # Le bien est lié à la pièce
            )
            
            db.session.add(nouveau_bien)
            db.session.flush() # Pour obtenir l'ID du nouveau_bien

            # 6. Gère l'upload de la facture
            fichier_facture = form.facture.data
            if fichier_facture:
                filename = secure_filename(fichier_facture.filename)
                
                # Crée un chemin unique pour éviter les conflits
                # ex: uploads/justificatifs/assure_5/bien_10_facture.pdf
                user_folder = os.path.join(app.config['UPLOAD_FOLDER'], f"assure_{current_user.id}")
                os.makedirs(user_folder, exist_ok=True)
                
                file_path = os.path.join(user_folder, f"bien_{nouveau_bien.id_bien}_{filename}")
                fichier_facture.save(file_path)
                
                # Enregistre le chemin relatif dans la DB
                relative_path = os.path.join(f"assure_{current_user.id}", f"bien_{nouveau_bien.id_bien}_{filename}")

                nouveau_justificatif = Justificatif(
                    chemin_fichier=relative_path,
                    type_justificatif="Facture",
                    # Lie le justificatif au bien (suppose une relation)
                    bien=nouveau_bien 
                )
                db.session.add(nouveau_justificatif)

            # 7. Valide la transaction
            db.session.commit()
            flash("Nouveau bien ajouté avec succès !", "success")
            # Redirige vers la page du logement ou le tableau de bord
            return redirect(url_for('mes_logements')) 

        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de l'ajout du bien : {e}", "danger")

    # 8. Si GET ou si le formulaire est invalide, on affiche la page
    #    On convertit les objets pour le template HTML (pour le script JS)
    liste_logement_pour_template = [{'id': l.id_logement, 'adresse': l.adresse} for l in user_logements]
    liste_pieces_pour_template = [{'id': p.id_piece, 'nom_piece': p.nom_piece, 'id_logement': p.id_logement} for p in user_pieces]
    
    return render_template(
        'ajouter_bien.html', 
        form=form, 
        liste_logement=liste_logement_pour_template, 
        liste_pieces=liste_pieces_pour_template
    )
    """
    return render_template(
        'ajouter_bien.html', 
        form=form, 
    )

@app.route('/bien/<int:bien_id>/')
@login_required
def voir_bien(bien_id):
    bien = Bien.query.get_or_404(bien_id)
    return render_template('info_bien.html', bien=bien)


# ------------------- MAIN -------------------
if __name__ == '__main__':
    app.run(debug=True)
