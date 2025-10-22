from monApp.database import Logement
def test_logement_repr(db_session):
    logement  = Logement(
        adresse="123 Rue de Test",
        type_logement="Appartement",
        surface=50.0,
        description="Appartement de test",
        id_assure=1
    )
    db_session.add(logement)
    db_session.commit()


    assert repr(logement) == f"<Logement ({logement.id_logement}) {logement.adresse}>"