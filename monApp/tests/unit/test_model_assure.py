from monApp.database import Assure, Assureur
from datetime import date

def test_assure_creation(db_session):
    # Il faut d'abord un assureur car Assure a une clé étrangère id_assureur
    assureur = Assureur(
        nom="Assur",
        prenom="Max",
        email="assureur.test@example.com",
        mot_de_passe="password123",
        telephone="0102030405",
        societe="MaSociete"
    )
    db_session.add(assureur)
    db_session.commit()

    assure = Assure(
        nom="Dupont",
        prenom="Jean",
        date_naissance=date(1990, 1, 1),
        email="jean.dupont@test.com",
        mdp_assure="securepass",
        telephone="0601020304",
        id_assureur=assureur.id_assureur
    )
    db_session.add(assure)
    db_session.commit()

    assert assure.id_assure is not None
    assert assure.nom == "Dupont"
    assert assure.email == "jean.dupont@test.com"