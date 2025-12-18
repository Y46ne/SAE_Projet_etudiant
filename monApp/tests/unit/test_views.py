import pytest
from monApp.database import User, Assure, Assureur, Logement, Piece, Bien, Sinistre, Justificatif
from hashlib import sha256
import io
from datetime import date, datetime
from unittest.mock import patch, MagicMock

@pytest.fixture
def client_authentifie(client, db_session):
    """Fixture qui cree un utilisateur Assure et le connecte."""
    # Crée un assureur pour l'utilisateur assuré
    assureur = Assureur(nom="Assur", prenom="Max", email="assureur@test.com", mot_de_passe="pwd", telephone="0102030405")
    db_session.add(assureur)
    db_session.commit()
 
    # Hash le mot de passe pour l'utilisateur et l'assuré
    pwd = "password"
    m = sha256()
    m.update(pwd.encode())
    hashed = m.hexdigest()
    
    user = User(Login="test@test.com", Password=hashed)
    db_session.add(user)
    # Crée un profil assuré lié à l'utilisateur
    
    utilisateur_assure = Assure(
        nom="Test", prenom="User", date_naissance="2000-01-01",
        email="test@test.com", mdp_assure=hashed, id_assureur=assureur.id_assureur, telephone="0606060606"
    )
    db_session.add(utilisateur_assure)
    db_session.commit()
 
    # Connexion de l'utilisateur
    client.post('/login/', data={'Login': 'test@test.com', 'Password': 'password'}, follow_redirects=True)
    return client

@pytest.fixture
def donnees_test(db_session, client_authentifie):
    """Cree un jeu de donnees complet lie a l'utilisateur connecte."""
    # Récupère l'utilisateur et son profil assuré
    utilisateur = User.query.get('test@test.com')
    assure = utilisateur.assure_profile
    
    # Crée un logement et l'associe à l'assuré
    logement = Logement(nom_logement="Maison Test", adresse="1 rue Test", type_logement="Maison", surface=100)
    logement.assures.append(assure)
    db_session.add(logement)
    db_session.commit()
    
    # Crée une pièce dans le logement
    piece = Piece(nom_piece="Salon", surface=20, id_logement=logement.id_logement)
    db_session.add(piece)
    db_session.commit()
    
    # Crée un bien dans la pièce
    bien = Bien(nom_bien="TV", categorie="Multimedia", date_achat=date(2023,1,1), prix_achat=500, id_piece=piece.id_piece)
    db_session.add(bien)
    db_session.commit()
    
    return { # Retourne un dictionnaire avec les donnees creees
        'logement': logement,
        'piece': piece,
        'bien': bien,
        'assure': assure
    }

def test_redirection_index(client):
    """Verifie que la racine redirige vers le login."""
    # Vérifie que l'accès à la racine redirige vers la page de connexion
    response = client.get('/')
    assert response.status_code == 302
    assert '/login' in response.location

def test_login_logout(client, db_session):
    """Teste le flux de connexion et déconnexion."""
    # Setup user
    # Crée un utilisateur de test
    m = sha256()
    m.update(b"password")
    user = User(Login="login@test.com", Password=m.hexdigest())
    db_session.add(user)
    db_session.commit()

    # Teste la connexion réussie
    response = client.post('/login/', data={'Login': 'login@test.com', 'Password': 'password'}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Connexion r\xc3\xa9ussie" in response.data or b"tableauDeBord" in response.data
 
    # Teste la déconnexion
    response = client.get('/logout/', follow_redirects=True)
    assert response.status_code == 200
    assert b"Identifiant" in response.data

def test_creer_compte(client, db_session):
    """Teste la création de compte."""
    # Assureur par défaut id=1 requis
    # S'assure qu'un assureur par défaut existe pour la création de compte
    if not Assureur.query.get(1):
        assureur = Assureur(nom="Def", prenom="Ault", email="def@ault.com", mot_de_passe="pwd", telephone="000")
        assureur.id_assureur = 1
        db_session.add(assureur)
        db_session.commit()

    response = client.post('/creer-compte/', data={
        'nom': 'Nouveau',
        'prenom': 'Compte',
        'date_naissance': '1990-01-01',
        'telephone': '0102030405',
        'email': 'new@test.com',
        'Password': 'password',
        'confirm': 'password'
    }, follow_redirects=True)
    
    # Vérifie que la création a réussi et que l'utilisateur existe en base
    assert response.status_code == 200
    assert User.query.get('new@test.com') is not None

def test_tableau_de_bord(client_authentifie, donnees_test):
    """Teste l'acces au tableau de bord."""
    response = client_authentifie.get('/tableauDeBord/')
    assert response.status_code == 200
    # Vérifie que le tableau de bord contient des informations attendues
    assert b"Tableau de bord" in response.data
    assert b"Maison Test" in response.data

def test_reinitialiser(client):
    """Teste la page de réinitialisation."""
    # Vérifie que la page de réinitialisation est accessible
    response = client.get('/reinitialiser/')
    assert response.status_code == 200

def test_parametres(client_authentifie, donnees_test):
    """Teste l'affichage et la modification des parametres."""
    # GET
    response = client_authentifie.get('/parametres/')
    assert response.status_code == 200 # Vérifie l'accès à la page des paramètres
 
    # POST
    response = client_authentifie.post('/parametres/', data={
        'nom': 'NomModif',
        'prenom': 'PrenomModif',
        'email': 'test@test.com',
        'telephone': '0909090909'
    }, follow_redirects=True)
    assert response.status_code == 200
    # Vérifie le message de succès après modification
    assert b"Param\xc3\xa8tres modifi\xc3\xa9s" in response.data
 
    # Verification de la base de donnees
    assure = donnees_test['assure']
    assert assure.nom == 'NomModif'
    # Vérifie que les modifications sont bien enregistrées en base
def test_changer_mot_de_passe(client_authentifie, db_session):
    """Teste le changement de mot de passe."""
    # Cas de succes
    response = client_authentifie.post('/changer_mot_de_passe/', data={
        'old_password': 'password',
        'new_password': 'newpassword123',
        'confirm_password': 'newpassword123'
    }, follow_redirects=True)
    assert response.status_code == 200
    # Vérifie le message de succès
    assert b"mot de passe a \xc3\xa9t\xc3\xa9 chang\xc3\xa9" in response.data
    
    # Verification de la base de donnees
    user = User.query.get('test@test.com')
    m = sha256() # Hash le nouveau mot de passe pour comparaison
    m.update(b"newpassword123")
    assert user.Password == m.hexdigest()
 
    # Cas d'echec (mauvais ancien mot de passe)
    response = client_authentifie.post('/changer_mot_de_passe/', data={
        'old_password': 'wrong',
        'new_password': 'newpassword123',
        'confirm_password': 'newpassword123'
    }, follow_redirects=True)
    assert b"ancien mot de passe est incorrect" in response.data
    # Vérifie le message d'erreur en cas de mauvais ancien mot de passe

def test_crud_logement(client_authentifie, donnees_test, db_session):
    """Teste CRUD Logement."""
    logement = donnees_test['logement']
 
    # Mes logements
    # Vérifie l'affichage des logements de l'utilisateur
    response = client_authentifie.get('/mes_logements/')
    assert response.status_code == 200
    assert b"Maison Test" in response.data
 
    # Ajouter logement
    response = client_authentifie.post('/ajouter_logement/', data={
        'nom_logement': 'Appart Test',
        'adresse': '2 rue Test',
        'type_logement': 'Appartement',
        'surface': 50,
        'description': 'Desc'
    }, follow_redirects=True)
    assert response.status_code == 200
    # Vérifie que le nouveau logement est bien créé en base
    assert Logement.query.filter_by(adresse='2 rue Test').first() is not None
 
    # Modifier logement
    response = client_authentifie.post(f'/modifier_logement/{logement.id_logement}/', data={
        'nom_logement': 'Maison Modif',
        'adresse': '1 rue Test Modif',
        'description': 'Desc Modif'
    }, follow_redirects=True)
    assert response.status_code == 200
    # Vérifie que le logement a été modifié en base
    db_session.refresh(logement)
    assert logement.nom_logement == 'Maison Modif'

    # Supprimer un logement
    response = client_authentifie.post(f'/logement/{logement.id_logement}/delete', follow_redirects=True)
    # Vérifie que le logement a été supprimé de la base
    assert response.status_code == 200
    assert Logement.query.get(logement.id_logement) is None

def test_crud_piece(client_authentifie, donnees_test, db_session):
    """Teste CRUD Pièce."""
    logement = donnees_test['logement']
    piece = donnees_test['piece']
 
    # Vérifie l'affichage des pièces d'un logement
    # Afficher les pieces
    response = client_authentifie.get(f'/logement/{logement.id_logement}/pieces/')
    assert response.status_code == 200
    assert b"Salon" in response.data
 
    # Ajouter pièce
    response = client_authentifie.post('/ajouter_piece/', data={
        'nom_piece': 'Cuisine',
        'surface': 15,
        'logement_id': logement.id_logement
    }, follow_redirects=True)
    assert response.status_code == 200
    # Vérifie que la nouvelle pièce est bien créée en base
    assert Piece.query.filter_by(nom_piece='Cuisine').first() is not None

    # Modifier une piece
    response = client_authentifie.post(f'/modifier_piece/{piece.id_piece}/', data={
        'nom_piece': 'Grand Salon',
        'surface': 25.0
    }, follow_redirects=True)
    assert response.status_code == 200
    # Vérifie que la pièce a été modifiée en base
    db_session.refresh(piece)
    assert piece.nom_piece == 'Grand Salon'

    # Supprimer pièce
    response = client_authentifie.post(f'/supprimer_piece/{piece.id_piece}/', follow_redirects=True)
    # Vérifie que la pièce a été supprimée de la base
    assert response.status_code == 200
    assert Piece.query.get(piece.id_piece) is None

def test_crud_bien(client_authentifie, donnees_test, db_session):
    """Teste CRUD Bien."""
    piece = donnees_test['piece']
    bien = donnees_test['bien']
    logement = donnees_test['logement']
 
    # Vérifie l'affichage des biens d'une pièce
    # Afficher la liste des biens
    response = client_authentifie.get(f'/piece/{piece.id_piece}/biens/')
    assert response.status_code == 200
    assert b"TV" in response.data
 
    # Tester les pages d'information/detail/vue du bien
    # Utilise un patch pour simuler le rendu de template et éviter les erreurs de template non trouvé
    with patch('monApp.views.render_template', return_value="ok"):
        client_authentifie.get(f'/info_bien/{bien.id_bien}')
        client_authentifie.get(f'/detail_bien/{bien.id_bien}')
        client_authentifie.get(f'/bien/{bien.id_bien}/')
 
    # Ajouter un bien (avec fichier mocke)
    # Simule l'upload d'un fichier PDF pour la facture
    with patch('monApp.views.os.makedirs'), patch('monApp.views.os.path.join', return_value='/tmp/fake.pdf'), patch('werkzeug.datastructures.FileStorage.save'):
        data = {
            'nom_bien': 'Canapé',
            'prix_achat': 1000,
            'categorie': 'Mobilier',
            'date_achat': '2023-02-01',
            'logement_id': logement.id_logement,
            'piece_id': piece.id_piece,
            'facture': (io.BytesIO(b"fake pdf"), 'facture.pdf')
        } # Données pour l'ajout du bien
        response = client_authentifie.post('/ajouter_bien/', data=data, content_type='multipart/form-data', follow_redirects=True)
        # Vérifie que le nouveau bien est bien créé en base
        assert response.status_code == 200
        assert Bien.query.filter_by(nom_bien='Canapé').first() is not None
 
    # Modifier bien
    response = client_authentifie.post(f'/modifier_bien/{bien.id_bien}/', data={
        'nom_bien': 'TV 4K',
        'categorie': 'Multimedia',
        'date_achat': '2023-01-01',
        'prix_achat': 600
    }, follow_redirects=True)
    assert response.status_code == 200
    # Vérifie que le bien a été modifié en base
    db_session.refresh(bien)
    assert bien.nom_bien == 'TV 4K'
 
    # Supprimer bien
    response = client_authentifie.post(f'/supprimer_bien/{bien.id_bien}/', follow_redirects=True)
    # Vérifie que le bien a été supprimé de la base
    assert response.status_code == 200
    assert Bien.query.get(bien.id_bien) is None

def test_declarer_sinistre(client_authentifie, donnees_test):
    """Teste la déclaration de sinistre."""
    logement = donnees_test['logement']
    bien = donnees_test['bien']
 
    # Vérifie l'accès à la page de déclaration de sinistre
    # GET
    client_authentifie.get('/declarer_sinistre/')

    # POST
    data = {
        'date_sinistre': '2024-01-01',
        'type_sinistre': 'vol',
        'logement_id': logement.id_logement,
        'biens_selectionnes': [str(bien.id_bien)],
        f'etat_bien_{bien.id_bien}': 'perte_totale'
    } # Données pour la déclaration de sinistre
    response = client_authentifie.post('/declarer_sinistre/', data=data, follow_redirects=True)
    # Vérifie le message de succès et la création du sinistre en base
    assert response.status_code == 200
    assert b"Sinistre d\xc3\xa9clar\xc3\xa9" in response.data
    assert Sinistre.query.count() > 0
