from .app import app, db, login_manager
from config import *
from flask import render_template, request, url_for, redirect, flash, jsonify
from monApp.database import User, Assure, Assureur, Logement, Piece, Bien, Sinistre, impacte
from monApp.forms import *
from flask_login import login_user, logout_user, login_required, current_user
from hashlib import sha256

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
            next_page = request.args.get('next') or url_for('dashboard')
            return redirect(next_page)
        else:
            flash('Identifiant ou mot de passe incorrect.', 'danger')
    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return "Vous etes sur le dashboard" 

@app.route('/reinitialiser/')
def reinitialiser():
    return render_template('reinitialiser.html')

@app.route('/tableauDeBord/')
def tableau_de_bord():
    return render_template('tableauDeBord.html')

@app.route('/creer-compte/', methods=['GET', 'POST'])
def creer_compte():
    form = SignUpForm()
    if form.validate_on_submit():
        try:
            new_user = User(
                Login=form.email.data,
                Password=sha256(form.Password.data.encode()).hexdigest(),
                role='client'
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Votre compte a été créé avec succès ! Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la création du compte : {e}', 'danger')
    return render_template('creeruncompte.html', form=form)

# ------------------- MAIN -------------------
if __name__ == '__main__':
    app.run(debug=True)
