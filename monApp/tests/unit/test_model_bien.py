from monApp.database import Bien, Piece, Logement
import datetime


def test_bien_repr(db_session):
    # Create minimal chain: Logement -> Piece -> Bien

    # Créer un User, un Assureur, puis un Assure pour satisfaire la contrainte id_assure
    from monApp.database import User, Assureur, Assure
    user = User(Login="bien@user", Password="pwd")
    db_session.add(user)
    assureur = Assureur(nom="NomA", prenom="PrenomA", email="a@a.com", mot_de_passe="pwd")
    db_session.add(assureur)
    db_session.commit()
    assure = Assure(nom="N", prenom="P", date_naissance=None, email=user.Login, mdp_assure="mdp", id_assureur=assureur.id_assureur)
    db_session.add(assure)
    db_session.commit()

    logement = Logement(adresse="123 Test", type_logement="Appartement", surface=40.0)
    logement.id_assure = assure.id_assure
    db_session.add(logement)
    db_session.commit()

    piece = Piece(nom_piece="Salon", type_piece="Salon", surface=20.0, etage=0, id_logement=logement.id_logement)
    db_session.add(piece)
    db_session.commit()

    bien = Bien(
        nom_bien="TestBien",
        id_piece=piece.id_piece,
        description="Description",
        categorie="Catégorie",
        date_achat=datetime.date(2020, 1, 1),
        prix_achat=100.0,
        etat="Neuf",
        valeur_actuelle=90.0,
    )
    db_session.add(bien)
    db_session.commit()

    assert repr(bien) == f"<Bien ({bien.id_bien}) {bien.nom_bien}>"

