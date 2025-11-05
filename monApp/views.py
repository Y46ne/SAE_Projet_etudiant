from .app import app, db, login_manager
from config import *
from flask import render_template, request, url_for, redirect, flash, jsonify
from monApp.database import User, Assure, Assureur, Logement, Piece, Bien, Sinistre, impacte
from monApp.forms import *
from flask_login import login_user, logout_user, login_required, current_user
from hashlib import sha256
from flask import abort

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)



@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = form.get_authenticated_user()
        if user:
            login_user(user)
            flash('Connexion réussie.', 'success')
            # rediriger vers le tableau de bord existant
            next_page = request.args.get('next') or url_for('tableau_de_bord')
            return redirect(next_page)
        else:
            flash('Identifiant ou mot de passe incorrect.', 'danger')
    return render_template('login.html', form=form)




@app.route('/reinitialiser/')
def reinitialiser():
    return render_template('reinitialiser.html')



@app.route('/tableauDeBord/')
def tableau_de_bord():
    return render_template('tableauDeBord.html')



@app.route('/ajouter_logement/')
def ajouter_logement():
    form = LogementForm()
    return render_template('ajouter_logement.html',form=form)


@app.route('/mes-logements/')
def mes_logements():
    logements = Logement.query.all()
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
@login_required
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
@login_required
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





# ------------------- MAIN -------------------
if __name__ == '__main__':
    app.run(debug=True)
