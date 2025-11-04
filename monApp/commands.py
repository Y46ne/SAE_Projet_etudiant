import click, logging as lg
from .app import app, db

@app.cli.command()
@click.argument('filename') 
def loaddb(filename):
    import yaml
    from .database import Assure, Assureur, Bien, Justificatif, Logement, Piece, Sinistre, User, couvre, possede, justifie, impacte
    from .app import db

    db.drop_all()
    db.create_all()

    with open(filename, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)

    from datetime import datetime, date
    from decimal import Decimal

    users = []
    for u in data.get('users', []):
        user = User(
            Login=u['Login'],
            Password=u['Password']
        )
        db.session.add(user)
        users.append(user)
    db.session.commit()

    assureurs = []
    for assr in data.get('assureurs', []):
        try:
            assureur = Assureur(
                nom=assr['nom'],
                prenom=assr['prenom'],
                email=assr['user_login'],
                login=assr['user_login'],
                mot_de_passe=assr['mot_de_passe'],
                telephone=assr.get('telephone'),
                societe=assr.get('societe')
            )
            db.session.add(assureur)
            assureurs.append(assureur)
        except Exception as e:
            print(f"Erreur création Assureur: {e} avec données: {assr}")
    db.session.commit()

    assures = []
    for a in data.get('assures', []):
        assure = Assure(
            nom=a['nom'],
            prenom=a['prenom'],
            date_naissance=date.fromisoformat(a['date_naissance']) if a.get('date_naissance') else None,
            email=a['user_login'],
            mdp_assure=a['mdp_assure'],
            telephone=a.get('telephone'),
            id_assureur=a['id_assureur']
        )
        db.session.add(assure)
        assures.append(assure)
    db.session.commit()

    logements = []
    for l in data.get('logements', []):
        logement = Logement(
            adresse=l['adresse'],
            type_logement=l.get('type_logement'),
            surface=Decimal(str(l['surface'])) if l.get('surface') is not None else None,
            description=l.get('description')
        )
        db.session.add(logement)
        logements.append(logement)
    db.session.commit()

    pieces = []
    for p in data.get('pieces', []):
        piece = Piece(
            nom_piece=p['nom_piece'],
            type_piece=p.get('type_piece'),
            surface=Decimal(str(p['surface'])) if p.get('surface') is not None else None,
            etage=p.get('etage'),
            id_logement=p['id_logement']
        )
        db.session.add(piece)
        pieces.append(piece)
    db.session.commit()

    biens = []
    for b in data.get('biens', []):
        bien = Bien(
            nom_bien=b['nom_bien'],
            description=b.get('description'),
            categorie=b.get('categorie'),
            date_achat=date.fromisoformat(b['date_achat']) if b.get('date_achat') else None,
            prix_achat=Decimal(str(b['prix_achat'])) if b.get('prix_achat') is not None else None,
            etat=b.get('etat'),
            valeur_actuelle=Decimal(str(b['valeur_actuelle'])) if b.get('valeur_actuelle') is not None else None,
            id_piece=b['id_piece']
        )
        db.session.add(bien)
        biens.append(bien)
    db.session.commit()

    justificatifs = []
    for j in data.get('justificatifs', []):
        justificatif = Justificatif(
            chemin_fichier=j['chemin_fichier'],
            type_justificatif=j.get('type_justificatif'),
            date_ajout=datetime.fromisoformat(j['date_ajout']) if j.get('date_ajout') else None
        )
        db.session.add(justificatif)
        justificatifs.append(justificatif)
    db.session.commit()

    sinistres = []
    for s in data.get('sinistres', []):
        sinistre = Sinistre(
            date_sinistre=date.fromisoformat(s['date_sinistre']) if s.get('date_sinistre') else None,
            type_sinistre=s.get('type_sinistre'),
            description=s.get('description'),
            montant_estime=Decimal(str(s['montant_estime'])) if s.get('montant_estime') is not None else None,
            numero_sinistre=s['numero_sinistre'],
            id_logement=s['id_logement']
        )
        db.session.add(sinistre)
        sinistres.append(sinistre)
    db.session.commit()

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
    '''Adds a new user''' 
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
from hashlib import sha256 
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
