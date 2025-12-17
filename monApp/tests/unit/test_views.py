import pytest
from monApp.database import User, Assure, Assureur, Logement, Piece, Bien, Sinistre, Justificatif
from hashlib import sha256
import io
from datetime import date, datetime
from unittest.mock import patch, MagicMock

@pytest.fixture
def auth_client(client, db_session):
    """Fixture qui crée un utilisateur Assuré et le connecte."""
    # Création Assureur (requis par FK)
    assureur = Assureur(nom="Assur", prenom="Max", email="assureur@test.com", mot_de_passe="pwd", telephone="0102030405")
    db_session.add(assureur)
    db_session.commit()

    # Création User et Assure
    pwd = "password"
    m = sha256()
    m.update(pwd.encode())
    hashed = m.hexdigest()
    
    user = User(Login="test@test.com", Password=hashed)
    db_session.add(user)
    
    assure = Assure(
        nom="Test", prenom="User", date_naissance="2000-01-01",
        email="test@test.com", mdp_assure=hashed, id_assureur=assureur.id_assureur, telephone="0606060606"
    )
    db_session.add(assure)
    db_session.commit()

    # Connexion
    client.post('/login/', data={'Login': 'test@test.com', 'Password': 'password'}, follow_redirects=True)
    return client

@pytest.fixture
def sample_data(db_session, auth_client):
    """Crée un jeu de données complet lié à l'utilisateur connecté."""
    user = User.query.get('test@test.com')
    assure = user.assure_profile
    
    logement = Logement(nom_logement="Maison Test", adresse="1 rue Test", type_logement="Maison", surface=100)
    logement.assures.append(assure)
    db_session.add(logement)
    db_session.commit()
    
    piece = Piece(nom_piece="Salon", surface=20, id_logement=logement.id_logement)
    db_session.add(piece)
    db_session.commit()
    
    bien = Bien(nom_bien="TV", categorie="Multimedia", date_achat=date(2023,1,1), prix_achat=500, id_piece=piece.id_piece)
    db_session.add(bien)
    db_session.commit()
    
    return {
        'logement': logement,
        'piece': piece,
        'bien': bien,
        'assure': assure
    }

def test_index_redirect(client):
    """Vérifie que la racine redirige vers le login."""
    response = client.get('/')
    assert response.status_code == 302
    assert '/login' in response.location

def test_login_logout(client, db_session):
    """Teste le flux de connexion et déconnexion."""
    # Setup user
    m = sha256()
    m.update(b"password")
    user = User(Login="login@test.com", Password=m.hexdigest())
    db_session.add(user)
    db_session.commit()

    # Login success
    response = client.post('/login/', data={'Login': 'login@test.com', 'Password': 'password'}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Connexion r\xc3\xa9ussie" in response.data or b"tableauDeBord" in response.data

    # Logout
    response = client.get('/logout/', follow_redirects=True)
    assert response.status_code == 200
    assert b"Identifiant" in response.data

def test_creer_compte(client, db_session):
    """Teste la création de compte."""
    # Assureur par défaut id=1 requis
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
    
    assert response.status_code == 200
    assert User.query.get('new@test.com') is not None

def test_tableau_de_bord(auth_client, sample_data):
    """Teste l'accès au tableau de bord."""
    response = auth_client.get('/tableauDeBord/')
    assert response.status_code == 200
    assert b"Tableau de bord" in response.data
    assert b"Maison Test" in response.data

def test_reinitialiser(client):
    """Teste la page de réinitialisation."""
    response = client.get('/reinitialiser/')
    assert response.status_code == 200

def test_parametres(auth_client, sample_data):
    """Teste l'affichage et la modification des paramètres."""
    # GET
    response = auth_client.get('/parametres/')
    assert response.status_code == 200
    
    # POST
    response = auth_client.post('/parametres/', data={
        'nom': 'NomModif',
        'prenom': 'PrenomModif',
        'email': 'test@test.com',
        'telephone': '0909090909'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Param\xc3\xa8tres modifi\xc3\xa9s" in response.data
    
    # Vérification DB
    assure = sample_data['assure']
    assert assure.nom == 'NomModif'

def test_changer_mot_de_passe(auth_client, db_session):
    """Teste le changement de mot de passe."""
    # Succès
    response = auth_client.post('/changer_mot_de_passe/', data={
        'old_password': 'password',
        'new_password': 'newpassword123',
        'confirm_password': 'newpassword123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"mot de passe a \xc3\xa9t\xc3\xa9 chang\xc3\xa9" in response.data
    
    # Vérification DB
    user = User.query.get('test@test.com')
    m = sha256()
    m.update(b"newpassword123")
    assert user.Password == m.hexdigest()

    # Echec (mauvais ancien mot de passe)
    response = auth_client.post('/changer_mot_de_passe/', data={
        'old_password': 'wrong',
        'new_password': 'newpassword123',
        'confirm_password': 'newpassword123'
    }, follow_redirects=True)
    assert b"ancien mot de passe est incorrect" in response.data

def test_logement_crud(auth_client, sample_data, db_session):
    """Teste CRUD Logement."""
    logement = sample_data['logement']
    
    # Mes logements
    response = auth_client.get('/mes_logements/')
    assert response.status_code == 200
    assert b"Maison Test" in response.data

    # Ajouter logement
    response = auth_client.post('/ajouter_logement/', data={
        'nom_logement': 'Appart Test',
        'adresse': '2 rue Test',
        'type_logement': 'Maison',
        'surface': 50,
        'description': 'Desc'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert Logement.query.filter_by(adresse='2 rue Test').first() is not None

    # Modifier logement
    response = auth_client.post(f'/modifier_logement/{logement.id_logement}/', data={
        'nom_logement': 'Maison Modif',
        'adresse': '1 rue Test Modif',
        'description': 'Desc Modif'
    }, follow_redirects=True)
    assert response.status_code == 200
    db_session.refresh(logement)
    assert logement.nom_logement == 'Maison Modif'

    # Supprimer logement
    response = auth_client.post(f'/logement/{logement.id_logement}/delete', follow_redirects=True)
    assert response.status_code == 200
    assert Logement.query.get(logement.id_logement) is None

def test_piece_crud(auth_client, sample_data, db_session):
    """Teste CRUD Pièce."""
    logement = sample_data['logement']
    piece = sample_data['piece']

    # Voir pièces
    response = auth_client.get(f'/logement/{logement.id_logement}/pieces/')
    assert response.status_code == 200
    assert b"Salon" in response.data

    # Ajouter pièce
    response = auth_client.post('/ajouter_piece/', data={
        'nom_piece': 'Cuisine',
        'surface': 15,
        'logement_id': logement.id_logement
    }, follow_redirects=True)
    assert response.status_code == 200
    assert Piece.query.filter_by(nom_piece='Cuisine').first() is not None

    # Modifier pièce
    response = auth_client.post(f'/modifier_piece/{piece.id_piece}/', data={
        'nom_piece': 'Grand Salon',
        'surface': 25
    }, follow_redirects=True)
    assert response.status_code == 200
    db_session.refresh(piece)
    assert piece.nom_piece == 'Grand Salon'

    # Supprimer pièce
    response = auth_client.post(f'/supprimer_piece/{piece.id_piece}/', follow_redirects=True)
    assert response.status_code == 200
    assert Piece.query.get(piece.id_piece) is None

def test_bien_crud(auth_client, sample_data, db_session):
    """Teste CRUD Bien."""
    piece = sample_data['piece']
    bien = sample_data['bien']
    logement = sample_data['logement']

    # Gestion bien (liste)
    response = auth_client.get(f'/piece/{piece.id_piece}/biens/')
    assert response.status_code == 200
    assert b"TV" in response.data

    # Info / Detail / Voir
    with patch('monApp.views.render_template', return_value="ok"):
        auth_client.get(f'/info_bien/{bien.id_bien}')
        auth_client.get(f'/detail_bien/{bien.id_bien}')
        auth_client.get(f'/bien/{bien.id_bien}/')

    # Ajouter bien (avec fichier mocké)
    with patch('monApp.views.os.makedirs'), patch('monApp.views.os.path.join', return_value='/tmp/fake.pdf'), patch('werkzeug.datastructures.FileStorage.save'):
        data = {
            'nom_bien': 'Canapé',
            'prix_achat': 1000,
            'categorie': 'Mobilier',
            'date_achat': '2023-02-01',
            'logement_id': logement.id_logement,
            'piece_id': piece.id_piece,
            'facture': (io.BytesIO(b"fake pdf"), 'facture.pdf')
        }
        response = auth_client.post('/ajouter_bien/', data=data, content_type='multipart/form-data', follow_redirects=True)
        assert response.status_code == 200
        assert Bien.query.filter_by(nom_bien='Canapé').first() is not None

    # Modifier bien
    response = auth_client.post(f'/modifier_bien/{bien.id_bien}/', data={
        'nom_bien': 'TV 4K',
        'categorie': 'Multimedia',
        'date_achat': '2023-01-01',
        'prix_achat': 600
    }, follow_redirects=True)
    assert response.status_code == 200
    db_session.refresh(bien)
    assert bien.nom_bien == 'TV 4K'

    # Supprimer bien
    response = auth_client.post(f'/supprimer_bien/{bien.id_bien}/', follow_redirects=True)
    assert response.status_code == 200
    assert Bien.query.get(bien.id_bien) is None

def test_declarer_sinistre(auth_client, sample_data):
    """Teste la déclaration de sinistre."""
    logement = sample_data['logement']
    bien = sample_data['bien']
    
    # GET
    auth_client.get('/declarer_sinistre/')

    # POST
    data = {
        'date_sinistre': '2024-01-01',
        'type_sinistre': 'vol',
        'logement_id': logement.id_logement,
        'biens_selectionnes': [str(bien.id_bien)],
        f'etat_bien_{bien.id_bien}': 'perte_totale'
    }
    response = auth_client.post('/declarer_sinistre/', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Sinistre d\xc3\xa9clar\xc3\xa9" in response.data
    assert Sinistre.query.count() > 0

def test_pdf_generation(auth_client, sample_data):
    """Teste les routes de génération PDF (avec mock)."""
    with patch('monApp.views.HTML') as mock_html:
        mock_instance = MagicMock()
        mock_html.return_value = mock_instance
        mock_instance.write_pdf.return_value = b"PDF CONTENT"

        # Page génération
        auth_client.get('/generation_rapport')

        # PDF Tous
        response = auth_client.get('/generer_pdf_tous')
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'application/pdf'

        # PDF Logement
        logement = sample_data['logement']
        response = auth_client.post('/generer_pdf_logement', data={'id_logement': logement.id_logement})
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'application/pdf'