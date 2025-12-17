from monApp.database import Bien, Piece, Logement
from datetime import date
from decimal import Decimal

def test_bien_creation(db_session):
    # Création de la hiérarchie nécessaire : Logement -> Pièce -> Bien
    logement = Logement(nom_logement="Maison Test", adresse="1 rue Test", type_logement="Maison", surface=100)
    db_session.add(logement)
    db_session.commit()
    
    piece = Piece(nom_piece="Salon", surface=20, id_logement=logement.id_logement)
    db_session.add(piece)
    db_session.commit()

    bien = Bien(
        nom_bien="Télévision",
        description="TV 4K",
        categorie="Multimedia",
        date_achat=date(2023, 1, 15),
        prix_achat=Decimal("500.00"),
        id_piece=piece.id_piece
        # Suppression de 'etat' qui causait l'erreur
    )
    db_session.add(bien)
    db_session.commit()

    assert bien.id_bien is not None
    assert bien.nom_bien == "Télévision"
    assert bien.prix_achat == 500.00