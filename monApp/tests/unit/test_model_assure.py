from monApp.database import Assure, Assureur

def test_assure_repr(db_session):
    assureur = Assureur(
        nom="Test",
        prenom="Assureur",
        email="test@assureur.com",
        telephone="0123456789",
        societe="TestAssur"
    )
    db_session.add(assureur)
    db_session.commit()

    assure = Assure(
        nom="DAL",
        prenom="Cricri",
        date_naissance="1990-01-01",
        email="cricri@dal.com",
        telephone="0123456789",
        id_assureur=assureur.id_assureur
    )
    db_session.add(assure)
    db_session.commit()

    assert repr(assure) == f"<Assure ({assure.id_assure}) Cricri DAL>"
