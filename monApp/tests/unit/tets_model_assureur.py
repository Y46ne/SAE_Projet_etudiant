from monApp.database import Assureur
def test_assureur_repr(db_session):
    assureur  = Assureur(
        nom="Test",
        prenom="Assureur",
        email="test@assureur.com",
        telephone="0123456789",
        societe="TestAssur"
    )
    db_session.add(assureur)
    db_session.commit()


    assert repr(assureur) == f"<Assureur ({assureur.id_assureur}) Test Assureur>"