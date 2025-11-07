from monApp.database import Piece, Logement
def test_piece_repr(db_session):
    piece  = Piece(
        nom_piece="Salle de bain",
        type_piece="Salle",
        surface=20.0,
        etage="1er",
        id_logement=1
    )
    db_session.add(piece)
    db_session.commit()


    assert repr(piece) == f"<Piece ({piece.id_piece}) {piece.nom_piece}>"