from monApp.database import Piece, Logement

def test_piece_creation(db_session):
    logement = Logement(nom_logement="L", adresse="A", type_logement="T", surface=50)
    db_session.add(logement)
    db_session.commit()

    piece = Piece(
        nom_piece="Cuisine",
        surface=12.0,
        id_logement=logement.id_logement
        # Suppression de 'etage' qui causait l'erreur
    )
    db_session.add(piece)
    db_session.commit()

    assert piece.id_piece is not None
    assert piece.nom_piece == "Cuisine"
    assert piece.surface == 12.0