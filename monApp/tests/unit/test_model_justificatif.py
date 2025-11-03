from monApp.database import Justificatif, Bien, Piece, Logement
import datetime


def test_justificatif_repr(db_session):
    # Create dependencies: Logement -> Piece -> Bien

    # Créer un User, un Assureur, puis un Assure pour satisfaire la contrainte id_assure
    from monApp.database import User, Assureur, Assure
    user = User(Login="justif@user", Password="pwd")
    db_session.add(user)
    assureur = Assureur(nom="NomA", prenom="PrenomA", email="a@a.com", mot_de_passe="pwd")
    db_session.add(assureur)
    db_session.commit()
    assure = Assure(nom="N", prenom="P", date_naissance=None, email=user.Login, mdp_assure="mdp", id_assureur=assureur.id_assureur)
    db_session.add(assure)
    db_session.commit()

    logement = Logement(adresse="Addr 1")
    db_session.add(logement)
    db_session.commit()

    piece = Piece(nom_piece="Chambre", id_logement=logement.id_logement)
    db_session.add(piece)
    db_session.commit()

    bien = Bien(nom_bien="B1", id_piece=piece.id_piece)
    db_session.add(bien)
    db_session.commit()

    justificatif = Justificatif(
        chemin_fichier="chemin/vers/le/fichier.pdf",
        type_justificatif="Justificatif de test",
        date_ajout=datetime.datetime(2023, 1, 1),
    )
    db_session.add(justificatif)
    db_session.commit()

    assert repr(justificatif) == f"<Justificatif {justificatif.id_justificatif} {justificatif.type_justificatif}>"
