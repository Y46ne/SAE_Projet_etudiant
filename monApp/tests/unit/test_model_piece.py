from monApp.database import Piece, Logement, Assure, Assureur, User


def test_piece_repr(db_session):
    # Create required Logement (which needs Assure)
    user = User(Login="u1", Password="p")
    db_session.add(user)
    assureur = Assureur(nom="AN", prenom="AP", email="a@a.com", mot_de_passe="m")
    db_session.add(assureur)
    db_session.commit()

    assure = Assure(nom="N", prenom="P", date_naissance=None, email=user.Login, mdp_assure="mdp", id_assureur=assureur.id_assureur)
    db_session.add(assure)
    db_session.commit()

    logement = Logement(adresse="Addr 2")
    logement.id_assure = assure.id_assure
    db_session.add(logement)
    db_session.commit()

    piece = Piece(nom_piece="Salle de bain", type_piece="Salle", surface=20.0, etage=1, id_logement=logement.id_logement)
    db_session.add(piece)
    db_session.commit()

    assert repr(piece) == f"<Piece {piece.id_piece} {piece.nom_piece}>"