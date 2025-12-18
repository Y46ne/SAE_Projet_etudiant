from monApp.database import Sinistre, Logement
from datetime import date
from decimal import Decimal

def test_sinistre_creation(db_session):
    logement = Logement(nom_logement="L", adresse="A", type_logement="T", surface=50)
    db_session.add(logement)
    db_session.commit()

    sinistre = Sinistre(
        numero_sinistre="SIN-2024-001",
        date_sinistre=date(2024, 3, 10),
        type_sinistre="Dégât des eaux",
        description="Fuite sous évier",
        montant_estime=Decimal("1200.00"),
        id_logement=logement.id_logement
    )
    db_session.add(sinistre)
    db_session.commit()

    assert sinistre.id_sinistre is not None
    assert sinistre.numero_sinistre == "SIN-2024-001"
    
    # Vérification générique du repr pour éviter les erreurs de formatage strict
    assert str(sinistre).startswith("<Sinistre")