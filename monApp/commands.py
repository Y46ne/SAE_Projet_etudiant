import click, logging as lg
from .app import app, db

@app.cli.command()
@click.argument('filename') 
def loaddb(filename):
    from .triggers.init_triggers import create_sinistre_montant_triggers
    import yaml
    from .database import User, Assure, Assureur, Logement, Piece, Bien, Sinistre, impacte
    from .app import db

    db.drop_all()
    db.create_all()

    with open(filename, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)

    users = []
    for u in data.get('users', []):
        user = User(**u)
        db.session.add(user)
        users.append(user)
    db.session.commit()

    assureurs = []
    for assr in data.get('assureurs', []):
        assureur = Assureur(nom=assr['nom'], prenom=assr['prenom'], email=assr['user_login'], telephone=assr['telephone'], societe=assr['societe'])
        db.session.add(assureur)
        assureurs.append(assureur)
    db.session.commit()

    assures = []
    for a in data.get('assures', []):
        # Assurez-vous que 'assureur_id' est présent dans votre fichier YAML pour les assurés
        assure = Assure(nom=a['nom'], prenom=a['prenom'], date_naissance=a['date_naissance'], email=a['user_login'], telephone=a['telephone'], id_assureur=a['id_assureur'])
        db.session.add(assure)
        assures.append(assure)
    db.session.commit()

    logements = []
    for l in data.get('logements', []):
        logement = Logement(**l)
        db.session.add(logement)
        logements.append(logement)
    db.session.commit()

    pieces = []
    for p in data.get('pieces', []):
        piece = Piece(**p)
        db.session.add(piece)
        pieces.append(piece)
    db.session.commit()

    biens = []
    for b in data.get('biens', []):
        bien = Bien(**b)
        db.session.add(bien)
        biens.append(bien)
    db.session.commit()

    sinistres = []
    for s in data.get('sinistres', []):
        sinistre = Sinistre(**s)
        db.session.add(sinistre)
        sinistres.append(sinistre)
    db.session.commit()

    conn = db.engine.connect()
    for i in data.get('impacte', []):
        conn.execute(impacte.insert().values(**i))
    conn.close() # Il est préférable de fermer la connexion après utilisation

    # Créer les triggers de base de données
    create_sinistre_montant_triggers()

    print("Base de données initialisée avec succès à partir de", filename)



@app.cli.command()
def syncdb():
    """
    Creates all missin tables
    """
    db.create_all()
    lg.warning("Database sunchronized!")


@app.cli.command()
@click.argument('login')
@click.argument('pwd')
def newuser (login, pwd):
    '''Adds a new user''' # Garder le docstring
    from .database import User
    from hashlib import sha256
    m = sha256()
    m.update(pwd.encode())
    unUser = User(Login=login ,Password =m.hexdigest())
    db.session.add(unUser)
    db.session.commit()
    lg.warning('User ' + login + ' created!')

import click
from .app import db
from hashlib import sha256 # Garder pour le hachage des mots de passe
from .database import User

@app.cli.command()
@click.argument('login')
@click.argument('pwd')
def newpassword(login, pwd):
    """Met à jour le mot de passe pour l'utilisateur donné."""
    user = User.query.get(login)
    if not user:
        click.echo(f"Utilisateur '{login}' introuvable.")
        return

    m = sha256()
    m.update(pwd.encode())
    user.Password = m.hexdigest()
    db.session.commit()

    click.echo(f"Mot de passe de l'utilisateur '{login}' mis à jour avec succès.")
