from monApp.database import Sinistre
def test_sinistre_repr(db_session):
    sinistre  = Sinistre(
        date_sinistre="2023-01-01",
        type_sinistre="Sinistre de test",
        description="Description du sinistre",
        numero_sinistre="123456",
        id_logement=1
    )
    db_session.add(sinistre)
    db_session.commit()

    assert repr(sinistre) == f"<Sinistre ({sinistre.id_sinistre}) {sinistre.numero_sinistre}>"