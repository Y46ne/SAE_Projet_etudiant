from monApp.database import User
import os

def test_syncdb(app):
    """Teste la commande syncdb."""
    runner = app.test_cli_runner()
    result = runner.invoke(args=['syncdb'])
    assert result.exit_code == 0
    assert "Database synchronized!" in result.output

def test_newuser(app, db_session):
    """Teste la création d'un utilisateur via CLI."""
    runner = app.test_cli_runner()
    result = runner.invoke(args=['newuser', 'cli_user', 'password123'])
    assert result.exit_code == 0
    assert "User cli_user created!" in result.output
    
    user = User.query.get('cli_user')
    assert user is not None

def test_newpassword(app, db_session):
    """Teste le changement de mot de passe via CLI."""
    # Création préalable
    u = User(Login='user_pwd', Password='old_password')
    db_session.add(u)
    db_session.commit()

    runner = app.test_cli_runner()
    result = runner.invoke(args=['newpassword', 'user_pwd', 'new_password'])
    assert result.exit_code == 0
    assert "Mot de passe de l'utilisateur 'user_pwd' mis à jour" in result.output

    db_session.refresh(u)
    assert u.Password != 'old_password'

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

    runner = app.test_cli_runner()
    result = runner.invoke(args=['loaddb', str(d)])
    assert result.exit_code == 0
    assert "Base de données initialisée" in result.output