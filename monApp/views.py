from flask import render_template, request, url_for, redirect, flash, make_response
from flask_login import (
    login_user, logout_user, login_required, current_user
)
from hashlib import sha256
from werkzeug.utils import secure_filename
import os

from .app import app, db, login_manager
from config import *
from monApp.database import User, Assure, Logement, Piece, Bien, Justificatif, Sinistre
from monApp.database.impacte import impacte as impacte_table
from monApp.forms import *
from .forms import ChangePasswordForm

# Import pour la génération de PDF
try:
    from weasyprint import HTML
except ImportError:
    HTML = None  # Gestion du cas où la librairie n'est pas installée
import datetime



@app.route('/')
def index():
    if current_user.is_authenticated:
        if not current_user.is_assureur :
            return redirect(url_for('tableau_de_bord'))
        else:
            return redirect(url_for('tableau_de_bord_assureur'))
    return redirect(url_for('login'))

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
            if not current_user.is_assureur :
                next_page = request.args.get('next') or url_for('tableau_de_bord')
                return redirect(next_page)
            else:
                next_page = request.args.get('next') or url_for('tableau_de_bord_assureur')
                return redirect(next_page)

        else:
            flash('Identifiant ou mot de passe incorrect.', 'danger')
    return render_template('login.html', form=unForm)

@app.route ("/logout/")
def logout():
    logout_user()
    return redirect ( url_for ('login'))

@app.route('/info_bien/<int:id>')
@login_required
def info_bien(id):
    bien = Bien.query.get_or_404(id)
    return render_template('info_bien.html', bien=bien)


@app.route('/reinitialiser/')
def reinitialiser():
    return render_template('reinitialiser.html')


@app.route('/tableauDeBord/')
@login_required
def tableau_de_bord():
    assure = current_user.assure_profile
    logements_bruts = []
    if assure:
        logements_bruts = assure.logements

    nb_logements_total = len(logements_bruts)
    nb_biens_total = 0
    valeur_totale_globale = 0.0
    logements_avec_stats = []

    for l in logements_bruts:
        nb_pieces_logement = len(l.pieces)
        nb_biens_logement = 0
        valeur_logement = 0.0

        for p in l.pieces:
            biens_de_la_piece = getattr(p, 'biens', [])
            nb_biens_logement += len(biens_de_la_piece)
            for b in biens_de_la_piece:
                if b.valeur_actuelle is not None:
                    try:
                        valeur_logement += float(b.valeur_actuelle)
                    except (ValueError, TypeError):
                        pass

        nb_biens_total += nb_biens_logement
        valeur_totale_globale += valeur_logement

        logements_avec_stats.append({
            'logement': l,
            'nb_pieces': nb_pieces_logement,
            'nb_biens': nb_biens_logement,
            'valeur_logement': valeur_logement
        })

    return render_template('tableauDeBord.html', 
                           nb_logements=nb_logements_total, 
                           nb_biens_total=nb_biens_total, 
                           valeur_totale=valeur_totale_globale, 
                           logements_stats=logements_avec_stats)

@app.route('/declarer_sinistre/', methods=['GET', 'POST'])
@login_required
def declarer_sinistre():
    form = DeclarerSinistre()
    form.type_sinistre.choices = [
        ('Dégât des eaux', 'Dégât des eaux'),
        ('Incendie', 'Incendie'),
        ('Vol', 'Vol'),
        ('Bris de glace', 'Bris de glace'),
        ('Catastrophe naturelle', 'Catastrophe naturelle'),
        ('Tempête', 'Tempête'),
        ('Dommages électriques', 'Dommages électriques'),
        ('Responsabilité civile', 'Responsabilité civile'),
        ('Autre', 'Autre')
    ]
    assure = current_user.assure_profile
    logements = assure.logements
    pieces = []
    biens = []
    for logement in logements:
        for piece in logement.pieces:
            pieces.append(piece)
            for bien in piece.biens:
                bien.valeur_actuelle = bien.calculer_valeur_actuelle()
                biens.append(bien)
    if form.validate_on_submit():
        # On récupère l'ID du logement choisi par l'utilisateur
        selected_logement_id = int(request.form.get("logement_id"))

        sinistre = Sinistre(
            date_sinistre=form.date_sinistre.data,
            type_sinistre=form.type_sinistre.data,
            description=form.description.data,
            numero_sinistre="SIN-" + datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
            id_logement=selected_logement_id
        )
        db.session.add(sinistre)
        db.session.flush() 

        biens_selectionnes = request.form.getlist("biens_selectionnes")
        total = 0
        
        for bien_id in biens_selectionnes:
            bien = Bien.query.get(int(bien_id))
            if not bien:
                continue

            if bien.piece.id_logement != selected_logement_id:
                print(f"Le bien {bien.id_bien} n'appartient pas au logement {selected_logement_id}")
                continue

            etat = request.form.get(f"etat_bien_{bien_id}")
            
            if etat == "perte_totale":
                degat = bien.valeur_actuelle or 0
            else:
                degat = (bien.valeur_actuelle or 0) * 0.5
            
            total += degat
            db.session.execute(impacte_table.insert().values(
                id_bien=bien.id_bien,
                id_sinistre=sinistre.id_sinistre,
                degat_estime=degat
            ))
            
        sinistre.montant_estime = total
        db.session.commit()
        flash("Sinistre déclaré avec succès", "success")
        return redirect(url_for("tableau_de_bord"))
    return render_template(
        "declarer_sinistre.html",
        form=form,
        logements=logements,
        pieces=pieces,
        biens=biens
    )

@app.route('/ajouter_logement/', methods=['GET', 'POST'])
@login_required
def ajouter_logement():
    form = LogementForm()
    if form.validate_on_submit():

        insertedLogement = Logement(
            nom_logement=form.nom_logement.data,
            adresse=form.adresse.data,
            type_logement=form.type_logement.data,
            surface=form.surface.data, 
            description=form.description.data
        )

        assure_connecte = current_user.assure_profile
        insertedLogement.assures.append(assure_connecte)

        db.session.add(insertedLogement)
        db.session.commit()
        
        print("-------------------------logement ajoute----------------------")

        return redirect(url_for('mes_logements'))

    print("-------------------------probleme----------------------")
    return render_template('ajouter_logement.html', form=form)

    

@app.route('/mes_logements/')
@login_required
def mes_logements():
    if current_user.assure_profile.logements == None:
        return render_template('mes_logements.html', logements=[])
    logements = current_user.assure_profile.logements
    rows = []
    for logement in logements:
        valeur_totale = 0
        nb_biens = 0
        for piece in logement.pieces:
            for bien in piece.biens:
                valeur_totale += bien.prix_achat or 0
                nb_biens += 1
        rows.append({
            'logement': logement,
            'nb_biens': nb_biens,
            'valeur': valeur_totale
        })
    return render_template('mes_logements.html', logements=rows)


@app.route('/logement/<int:id>/pieces/')
@login_required
def view_logement_pieces(id):
    logement = Logement.query.get_or_404(id)
    return render_template('logement_pieces.html', logement=logement)


@app.route('/piece/<int:piece_id>/biens/')
@login_required
def gestion_bien(piece_id):
    piece = Piece.query.get_or_404(piece_id)
    biens = Bien.query.filter_by(id_piece=piece.id_piece).all()
    # Met à jour la valeur actuelle pour chaque bien si besoin
    for bien in biens:
        bien.valeur_actuelle = bien.calculer_valeur_actuelle()
    return render_template('gestion_bien.html', piece=piece, biens=biens)


@app.route('/creer-compte/', methods=['GET', 'POST'])
def creer_compte():
    form = SignUpForm()
    if form.validate_on_submit():
        try:
            new_user = User(
                Login=form.email.data,
                Password=sha256(form.Password.data.encode()).hexdigest()
            )
            new_assure = Assure(
                nom=form.nom.data,
                prenom=form.prenom.data,
                date_naissance=form.date_naissance.data,
                telephone=form.telephone.data,
                email=form.email.data,
                mdp_assure= form.Password.data,
                id_assureur= 1
            )
            db.session.add(new_user)
            db.session.add(new_assure)
            db.session.commit()
            flash('Votre compte a été créé avec succès ! Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la création du compte : {e}', 'danger')
    return render_template('creeruncompte.html', form=form)
    
@app.route('/detail_bien/<int:id>')
@login_required
def detail_bien(id):
    bien = Bien.query.get_or_404(id)
    return render_template('detail_bien.html', bien=bien)


@app.route('/parametres/', methods=['GET', 'POST'])
@login_required
def parametres():
    user = current_user
    if user.is_assureur:
        return redirect(url_for('parametres_assureur'))
    
    assure = current_user.assure_profile
    if assure is None:
        flash("Profil d'assuré introuvable.", "danger")
        return redirect(url_for('tableau_de_bord'))
        
    print("Assure utilisé :", assure.nom, assure.prenom, assure.email, assure.telephone)
    form = ParametresForm(obj=assure)
    if form.validate_on_submit():
        assure.nom = form.nom.data
        assure.prenom = form.prenom.data
        assure.telephone = form.telephone.data
        try:
            db.session.commit()
            flash("Paramètres modifiés avec succès.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de la modification : {e}", "danger")
    return render_template('parametres.html', form=form)


@app.route('/changer_mot_de_passe/', methods=['GET', 'POST'])
@login_required
def changer_mot_de_passe():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        
        m_old = sha256()
        m_old.update(form.old_password.data.encode())
        old_password_hashed = m_old.hexdigest()
        
        is_correct = False
        if old_password_hashed == current_user.Password:
            is_correct = True
        elif form.old_password.data == current_user.Password:
            is_correct = True
        
        if not is_correct:
            flash("L'ancien mot de passe est incorrect.", "danger")
            return render_template('changer_mot_de_passe.html', form=form)
            
        try:
            m_new = sha256()
            m_new.update(form.new_password.data.encode())
            new_password_hashed = m_new.hexdigest()
            
            current_user.Password = new_password_hashed
            
            if current_user.assure_profile:
                current_user.assure_profile.mdp_assure = new_password_hashed
            elif current_user.assureur_profile:
                current_user.assureur_profile.mot_de_passe = new_password_hashed

            db.session.commit()
            flash('Votre mot de passe a été changé avec succès.', 'success')

            return redirect(url_for('parametres')) 
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors du changement de mot de passe : {e}', 'danger')
    return render_template('changer_mot_de_passe.html', form=form)


@app.route('/ajouter_piece/', methods=['GET', 'POST'])
@login_required
def ajouter_piece():
    form = PieceForm()
    logements = current_user.assure_profile.logements
    form.logement_id.choices = [(l.id_logement, l.nom_logement) for l in logements]

    if form.validate_on_submit():
        try:
            nouvelle_piece = Piece(
                nom_piece=form.nom_piece.data,
                surface=form.surface.data,
                id_logement=form.logement_id.data
            )
            db.session.add(nouvelle_piece)
            db.session.commit()
            flash("Nouvelle pièce ajoutée avec succès !", "success")
            return redirect(url_for('mes_logements'))
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de l'ajout de la pièce : {e}", "danger")
    if form.errors:
        print("Erreurs du formulaire :", form.errors)
    return render_template('ajouter_piece.html', form=form)

@app.route('/ajouter_bien/', methods=['GET', 'POST'])
@login_required
def ajouter_bien():

    form = AjouterBienForm()
    assure_profil = current_user.assure_profile
    user_logements = assure_profil.logements
    
    user_pieces = []
    for log in user_logements:
        user_pieces.extend(log.pieces)

    form.logement_id.choices = [(l.id_logement, l.nom_logement) for l in user_logements]
    form.piece_id.choices = [(p.id_piece, p.nom_piece) for p in user_pieces]

    if form.validate_on_submit():
        try:
            fichier_facture = form.facture.data
            if not fichier_facture:
                flash("L'ajout d'un justificatif est obligatoire.", "danger")
            else:
                filename = secure_filename(fichier_facture.filename)
                file_ext = os.path.splitext(filename)[1].lower()

                if file_ext not in ['.pdf', '.png', '.jpg', '.jpeg']:
                    flash("Format de fichier non supporté. Veuillez utiliser PDF, PNG, JPG ou JPEG.", "danger")
                else:
                    nouveau_bien = Bien(
                        nom_bien=form.nom_bien.data,
                        prix_achat=form.prix_achat.data,
                        categorie=form.categorie.data,
                        date_achat=form.date_achat.data,
                        id_piece=form.piece_id.data
                    )
                    
                    db.session.add(nouveau_bien)
                    db.session.flush() 

                    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], f"assure_{current_user.id_assure}")
                    os.makedirs(user_folder, exist_ok=True)
                    
                    file_path = os.path.join(user_folder, f"bien_{nouveau_bien.id_bien}_{filename}")
                    fichier_facture.save(file_path)
                    
                    relative_path = os.path.join(f"assure_{current_user.id_assure}", f"bien_{nouveau_bien.id_bien}_{filename}")

                    nouveau_justificatif = Justificatif(
                        chemin_fichier=relative_path,
                        type_justificatif="Facture",
                        id_bien=nouveau_bien.id_bien
                    )
                    db.session.add(nouveau_justificatif)

                    db.session.commit()
                    flash("Nouveau bien ajouté avec succès !", "success")
                    # Récupérer la pièce et le logement associés
                    piece = Piece.query.get(nouveau_bien.id_piece)
                    if piece:
                        return redirect(url_for('gestion_bien', piece_id=piece.id_piece))
                    else:
                        return redirect(url_for('mes_logements'))

        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de l'ajout du bien : {e}", "danger")

    liste_logement_pour_template = [{'id': l.id_logement, 'nom': l.nom_logement, 'adresse': l.adresse} for l in user_logements]
    liste_pieces_pour_template = [{'id': p.id_piece, 'nom_piece': p.nom_piece, 'id_logement': p.id_logement} for p in user_pieces]
    
    return render_template(
        'ajouter_bien.html', 
        form=form, 
        liste_logement=liste_logement_pour_template, 
        liste_pieces=liste_pieces_pour_template
    )

@app.route('/bien/<int:bien_id>/')
@login_required
def voir_bien(bien_id):
    bien = Bien.query.get_or_404(bien_id)
    return render_template('info_bien.html', bien=bien)


@app.route('/modifier_logement/<int:logement_id>/', methods=['GET', 'POST'])
@login_required
def modifier_logement(logement_id):
    logement = Logement.query.get_or_404(logement_id)
    form = ModifierLogementForm(obj=logement)
    if form.validate_on_submit():
        logement.nom_logement = form.nom_logement.data
        logement.adresse = form.adresse.data
        logement.description = form.description.data
        try:
            db.session.commit()
            flash("Logement modifié avec succès.", "success")
            return redirect(url_for('mes_logements'))
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de la modification : {e}", "danger")
    return render_template('modifier_logement.html', form=form, logement=logement)

@app.route('/modifier_piece/<int:piece_id>/', methods=['GET', 'POST'])
@login_required
def modifier_piece(piece_id):
    piece = Piece.query.get_or_404(piece_id)
    form = ModifierPieceForm(obj=piece)
    if form.validate_on_submit():
        piece.nom_piece = form.nom_piece.data
        piece.surface = form.surface.data
        try:
            db.session.commit()
            flash("Pièce modifiée avec succès.", "success")
            return redirect(url_for('view_logement_pieces', id=piece.id_logement))
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de la modification : {e}", "danger")
    return render_template('modifier_piece.html', form=form, piece=piece)

@app.route('/supprimer_piece/<int:piece_id>/', methods=['POST', 'GET'])
@login_required
def supprimer_piece(piece_id):
    piece = Piece.query.get_or_404(piece_id)
    try:
        for bien in piece.biens:
            db.session.delete(bien)
        db.session.delete(piece)
        db.session.commit()
        flash("Pièce et tous ses biens supprimés avec succès.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur lors de la suppression : {e}", "danger")
    return redirect(url_for('view_logement_pieces', id=piece.id_logement))

@app.route('/logement/<int:id>/delete', methods=['POST'])
@login_required
def delete_logement(id):
    logement = Logement.query.get_or_404(id)
    try:
        for sinistre in logement.sinistres:
            db.session.delete(sinistre)
        for piece in logement.pieces:
            for bien in piece.biens:
                db.session.delete(bien)
            db.session.delete(piece)
        db.session.delete(logement)
        db.session.commit()
        flash('Logement et toutes ses pièces et biens supprimés.', 'success')
    except Exception as e:
        db.session.rollback()
        print("Erreur suppression :", e)
        flash(f'Erreur lors de la suppression : {e}', 'danger')
    return redirect(url_for('mes_logements'))

@app.route('/modifier_bien/<int:bien_id>/', methods=['GET', 'POST'])
@login_required
def modifier_bien(bien_id):
    bien = Bien.query.get_or_404(bien_id)
    form = ModifierBienForm(obj=bien)

    if form.validate_on_submit():
        bien.nom_bien = form.nom_bien.data
        bien.categorie = form.categorie.data
        bien.date_achat = form.date_achat.data
        bien.prix_achat = form.prix_achat.data
        try:
            db.session.commit()
            flash("Bien modifié avec succès.", "success")
            piece = Piece.query.get(bien.id_piece)
            if piece:
                return redirect(url_for('gestion_bien', piece_id=piece.id_piece))
            else:
                return redirect(url_for('mes_logements'))
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de la modification : {e}", "danger")
    return render_template('modifier_bien.html', form=form, bien=bien)

@app.route('/supprimer_bien/<int:bien_id>/', methods=['POST'])
@login_required
def supprimer_bien(bien_id):
    bien = Bien.query.get_or_404(bien_id)
    piece_id = bien.id_piece
    try:
        db.session.delete(bien)
        db.session.commit()
        flash("Bien supprimé avec succès.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur lors de la suppression : {e}", "danger")
    return redirect(url_for('gestion_bien', piece_id=piece_id))


# Fonction utilitaire pour préparer les données du rapport
def get_rapport_data(logements):
    rapport_data = []
    total_global = 0.0
    
    for logement in logements:
        logement_data = {
            'logement': logement,
            'pieces': [],
            'total_logement': 0.0
        }
        
        # On trie les pièces pour un affichage ordonné
        pieces_sorted = sorted(logement.pieces, key=lambda x: x.nom_piece)
        
        for piece in pieces_sorted:
            piece_data = {
                'piece': piece,
                'categories': {},
                'total_piece': 0.0
            }
            
            for bien in piece.biens:
                valeur = bien.calculer_valeur_actuelle()
                if valeur is None:
                    valeur = 0.0
                
                cat = bien.categorie if bien.categorie else "Autre"
                
                if cat not in piece_data['categories']:
                    piece_data['categories'][cat] = {'biens': [], 'total': 0.0}
                
                # On prépare un dictionnaire simple pour le template
                bien_info = {
                    'nom': bien.nom_bien,
                    'date_achat': bien.date_achat,
                    'prix_achat': bien.prix_achat,
                    'valeur_actuelle': valeur
                }
                
                piece_data['categories'][cat]['biens'].append(bien_info)
                piece_data['categories'][cat]['total'] += valeur
                piece_data['total_piece'] += valeur
            
            # On n'ajoute la pièce que si elle contient quelque chose
            if piece_data['categories']:
                 logement_data['pieces'].append(piece_data)
                 logement_data['total_logement'] += piece_data['total_piece']
        
        rapport_data.append(logement_data)
        total_global += logement_data['total_logement']
        
    return rapport_data, total_global

@app.route('/generation_rapport')
@login_required
def generation_rapport():
    logements = current_user.assure_profile.logements
    return render_template('generation_rapport.html', logements=logements)

@app.route('/generer_pdf_tous')
@login_required
def generer_pdf_tous():
    if not HTML:
        flash("Erreur : La librairie WeasyPrint n'est pas installée.", "danger")
        return redirect(url_for('generation_rapport'))
        
    logements = current_user.assure_profile.logements
    data, total = get_rapport_data(logements)
    
    html = render_template('pdf_rapport.html', data=data, total_global=total, title="Rapport Global", date_generation=datetime.date.today().strftime('%d/%m/%Y'))
    pdf = HTML(string=html).write_pdf()
    
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=rapport_global.pdf'
    return response

@app.route('/generer_pdf_logement', methods=['POST'])
@login_required
def generer_pdf_logement():
    if not HTML:
        flash("Erreur : La librairie WeasyPrint n'est pas installée.", "danger")
        return redirect(url_for('generation_rapport'))

    id_logement = request.form.get('id_logement')
    if not id_logement:
        flash("Veuillez sélectionner un logement.", "warning")
        return redirect(url_for('generation_rapport'))

    logement = Logement.query.get_or_404(id_logement)
    
    # Vérification de sécurité
    if logement not in current_user.assure_profile.logements:
        flash("Accès interdit à ce logement.", "danger")
        return redirect(url_for('generation_rapport'))
        
    data, total = get_rapport_data([logement])
    
    html = render_template('pdf_rapport.html', data=data, total_global=total, title=f"Rapport - {logement.adresse}", date_generation=datetime.date.today().strftime('%d/%m/%Y'))
    pdf = HTML(string=html).write_pdf()
    
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=rapport_logement_{id_logement}.pdf'
    return response









#------Partie assureur------
@app.route('/tableau_de_bord_assureur/')
@login_required
def tableau_de_bord_assureur():
    if not current_user.assureur_profile:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))

    assureur = current_user.assureur_profile
    
    assures = Assure.query.filter_by(id_assureur=assureur.id_assureur).all()

    all_logements = []
    for assure in assures:
        all_logements.extend(assure.logements)


    logement_ids = [l.id_logement for l in all_logements]
    sinistres = Sinistre.query.filter(Sinistre.id_logement.in_(logement_ids)).order_by(Sinistre.date_sinistre.desc()).all()

    sinistres_en_attente = len([s for s in sinistres if s.statut == 'Déclaré'])
    expertises_a_valider = len([s for s in sinistres if s.statut == 'Expertisé'])
    total_demandes = len(sinistres)

    valeur_totale = 0
    for logement in all_logements:
        for piece in logement.pieces:
            for bien in piece.biens:
                if bien.valeur_actuelle:
                    valeur_totale += bien.valeur_actuelle

    return render_template('assureur/tableau_bord_assureur.html',
                           sinistres_en_attente=sinistres_en_attente,
                           expertises_a_valider=expertises_a_valider,
                           total_demandes=total_demandes,
                           valeur_totale=valeur_totale,
                           sinistres=sinistres)

@app.route('/liste_sinistres/')
@login_required
def liste_sinistres():
    if not current_user.assureur_profile:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    assureur = current_user.assureur_profile
    assures = Assure.query.filter_by(id_assureur=assureur.id_assureur).all()
    all_logements = []
    for assure in assures:
        all_logements.extend(assure.logements)
    logement_ids = [l.id_logement for l in all_logements]
    sinistres = Sinistre.query.filter(Sinistre.id_logement.in_(logement_ids)).order_by(Sinistre.date_sinistre.desc()).all()
    return render_template('assureur/liste_sinistres.html', sinistres=sinistres)

@app.route('/liste_assures/')
@login_required
def liste_assures():
    if not current_user.assureur_profile:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))

    assureur = current_user.assureur_profile
    assures = Assure.query.filter_by(id_assureur=assureur.id_assureur).all()

    return render_template('assureur/liste_assures.html', assures=assures)


@app.route('/parametres_assureur/')
@login_required
def parametres_assureur():
    if not current_user.assureur_profile:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    
    assureur = current_user.assureur_profile
    form = ParametresForm(obj=assureur)

    if form.validate_on_submit():
        assureur.nom = form.nom.data
        assureur.prenom = form.prenom.data
        assureur.telephone = form.telephone.data
        try:
            db.session.commit()
            flash("Paramètres modifiés avec succès.", "success")
            return redirect(url_for('parametres_assureur'))
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de la modification : {e}", "danger")
    
    return render_template('assureur/parametres_assureur.html', form=form)

@app.route('/detail_sinistre/<int:id>', methods=['GET', 'POST'])
@login_required
def detail_sinistre(id):
    if not current_user.assureur_profile:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    sinistre = Sinistre.query.get_or_404(id)
    form = UpdateSinistreForm(obj=sinistre)

    if form.validate_on_submit():
        sinistre.statut = form.statut.data
        sinistre.montant_estime = form.montant_estime.data
        sinistre.montant_final = form.montant_final.data
        try:
            db.session.commit()
            flash("Sinistre mis à jour avec succès.", "success")
            return redirect(url_for('detail_sinistre', id=sinistre.id_sinistre))
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de la mise à jour : {e}", "danger")
    
    logement = sinistre.logement
    assure = logement.assures[0] if logement.assures else None

    return render_template('assureur/detail_sinistre.html', sinistre=sinistre, form=form, logement=logement, assure=assure)

@app.route('/detail_assure/<int:id>')
@login_required
def detail_assure(id):
    if not current_user.assureur_profile:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    assure = Assure.query.get_or_404(id)
    total_valeur_biens = 0.0

    if assure.date_naissance:
        if isinstance(assure.date_naissance, str):
            try:
                assure.date_naissance = datetime.datetime.strptime(assure.date_naissance, '%Y-%m-%d').date()
            except ValueError:
                assure.date_naissance = None
    
    sinistres = []
    for logement in assure.logements:
        sinistres.extend(logement.sinistres)
        for piece in logement.pieces:
            for bien in piece.biens:
                if bien.valeur_actuelle is not None:
                    try:
                        total_valeur_biens += float(bien.valeur_actuelle)
                    except (ValueError, TypeError):
                        pass
                        
    return render_template('assureur/detail_assure.html', assure=assure, total_valeur_biens=total_valeur_biens, sinistres=sinistres)


# ------------------- MAIN -------------------
if __name__ == '__main__':
    app.run(debug=True)