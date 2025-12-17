from monApp.database import User
import os

#Site utilisé pour trouver comment faire des tests de commandes : 
# https://flask.palletsprojects.com/en/stable/testing/



def test_syncdb(app):
    """Teste la commande syncdb."""
    coureur = app.test_cli_runner()
    resultat = coureur.invoke(args=['syncdb'])
    print(resultat)
    assert resultat.exit_code == 0
    assert "Database synchronized!" in resultat.output

def test_newuser(app, db_session):
    """Teste la création d'un utilisateur via CLI."""
    coureur = app.test_cli_runner()
    resultat = coureur.invoke(args=['newuser', 'cli', 'password123'])
    print(resultat)

    assert resultat.exit_code == 0
    assert "User cli created!" in resultat.output
    
    utilisateur = User.query.get('cli')
    assert utilisateur is not None

def test_newpassword(app, db_session):
    """Teste le changement de mot de passe via CLI."""
    utilisateur = User(Login='user_pwd', Password='old_password')
    db_session.add(utilisateur)
    db_session.commit()

    coureur = app.test_cli_runner()
    resultat = coureur.invoke(args=['newpassword', 'user_pwd', 'new_password'])
    print(resultat)

    assert resultat.exit_code == 0
    assert "Mot de passe de l'utilisateur 'user_pwd' mis à jour" in resultat.output

    db_session.refresh(utilisateur)
    assert utilisateur.Password != 'old_password'

def test_loaddb(app, db_session, tmp_path):
    """Teste le chargement de données depuis un YAML."""
    # Création d'un fichier YAML temporaire
    d = tmp_path / "data_test.yml"
    d.write_text("""
users: []
assureurs:
  - nom: "Test"
    prenom: "Assureur"
    email: "test@loaddb.com"
    mot_de_passe: "pass"
    telephone: "0102030405"
""", encoding='utf-8')

    coureur = app.test_cli_runner()
    resultat = coureur.invoke(args=['loaddb', str(d)])
    print(resultat)

    assert resultat.exit_code == 0
    assert "Base de données initialisée" in resultat.output