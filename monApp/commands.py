import click
from .app import app, db
import yaml
from datetime import datetime, date
from decimal import Decimal

from .database import Assure, Assureur, Bien, Justificatif, Logement, Piece, Sinistre, User
from .database.couvre import couvre
from .database.possede import possede
from .database.justifie import justifie
from .database.impacte import impacte

@app.cli.command()
@click.argument('filename')
def loaddb(filename):
    """Charge les données depuis un fichier YAML dans la base de données."""
    
    db.drop_all()
    db.create_all()

    with open(filename, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    # ---- USERS ----
    for a in data.get('assureurs', []):
        m = sha256()
        m.update(a['mot_de_passe'].encode())
        user = User(
            Login=a['email'],
            Password=m.hexdigest()
        )
        db.session.add(user)
    db.session.commit()
    for a in data.get('assures', []):
        m = sha256()
        m.update(a['mdp_assure'].encode())
        user = User(
            Login=a['user_login'],
            Password=m.hexdigest()
        )
        db.session.add(user)
    db.session.commit()

    # ---- ASSUREURS ----
    for assr in data.get('assureurs', []):
        assureur = Assureur(
            nom=assr['nom'],
            prenom=assr['prenom'],
            email=assr['email'],  # email
            mot_de_passe=assr['mot_de_passe'],
            telephone=assr.get('telephone'),
            societe=assr.get('societe'),
        )
        db.session.add(assureur)
    db.session.commit()

    # ---- ASSURES ----
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
    db.session.commit()

    # ---- LOGEMENTS ----
    for l in data.get('logements', []):
        logement = Logement(
            adresse=l['adresse'],
            type_logement=l.get('type_logement'),
            surface=Decimal(str(l['surface'])) if l.get('surface') is not None else None,
            description=l.get('description')
        )
        db.session.add(logement)
    db.session.commit()

    # ---- PIECES ----
    for p in data.get('pieces', []):
        piece = Piece(
            nom_piece=p['nom_piece'],
            surface=Decimal(str(p['surface'])) if p.get('surface') is not None else None,
            id_logement=p['id_logement']
        )
        db.session.add(piece)
    db.session.commit()

    # ---- BIENS ----
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
    db.session.commit()

    # ---- JUSTIFICATIFS ----
    for j in data.get('justificatifs', []):
        justificatif = Justificatif(
            chemin_fichier=j['chemin_fichier'],
            type_justificatif=j.get('type_justificatif'),
            date_ajout=datetime.fromisoformat(j['date_ajout']) if j.get('date_ajout') else None
        )
        db.session.add(justificatif)
    db.session.commit()

    # ---- SINISTRES ----
    for s in data.get('sinistres', []):
        sinistre = Sinistre(
            date_sinistre=date.fromisoformat(s['date_sinistre']) if s.get('date_sinistre') else None,
            type_sinistre=s.get('type_sinistre'),
            description=s.get('description'),
            montant_estime=Decimal(str(s['montant_estime'])) if s.get('montant_estime') is not None else None,
            montant_final=Decimal(str(s['montant_final'])) if s.get('montant_final') is not None else None,
            numero_sinistre=s['numero_sinistre'],
            date_declaration=date.fromisoformat(s['date_declaration']) if s.get('date_declaration') else None,
            statut=s.get('statut', 'Déclaré'),
            id_logement=s['id_logement']
        )
        db.session.add(sinistre)
    db.session.commit()

    # Couvre
    for c in data.get('couvre', []):
        if 'date_debut' in c and isinstance(c['date_debut'], str):
            c['date_debut'] = datetime.fromisoformat(c['date_debut']).date()
        db.session.execute(couvre.insert().values(**c))

    # Justifie
    for j in data.get('justifie', []):
        db.session.execute(justifie.insert().values(**j))

    # Impacte
    for i in data.get('impacte', []):
        db.session.execute(impacte.insert().values(**i))

    # Possede
    for p in data.get('possede', []):
        assure = Assure.query.get(p['id_assure'])
        logement = Logement.query.get(p['id_logement'])

        if assure and logement:
            assure.logements.append(logement)
        else:
            print(f"Assure {p['id_assure']} ou Logement {p['id_logement']} n'existe pas.")

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
def newuser(login, pwd):
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
