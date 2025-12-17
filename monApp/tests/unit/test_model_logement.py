from monApp.database import Logement
from decimal import Decimal

def test_logement_creation(db_session):
    logement = Logement(
        nom_logement="Appartement Centre",
        adresse="10 rue de la Paix",
        type_logement="Appartement",
        surface=Decimal("55.5"),
        description="Bel appart"
        # Suppression de id_assure (relation Many-to-Many gérée via 'possede')
    )
    db_session.add(logement)
    db_session.commit()

    assert logement.id_logement is not None
    assert logement.nom_logement == "Appartement Centre"