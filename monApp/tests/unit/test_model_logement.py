from monApp.database import Logement, Assure, Assureur, User


def test_logement_repr(db_session):
    # Create Assureur, User and Assure required by Logement
    user = User(Login="owner@login", Password="pwd")
    db_session.add(user)

    assureur = Assureur(nom="NomA", prenom="PrenomA", email="a@a.com", mot_de_passe="pwd")
    db_session.add(assureur)
    db_session.commit()

    assure = Assure(nom="N", prenom="P", date_naissance=None, email=user.Login, mdp_assure="mdp", id_assureur=assureur.id_assureur)
    db_session.add(assure)
    db_session.commit()


    logement = Logement(adresse="123 Rue de Test", type_logement="Appartement", surface=50.0, description="Appartement de test")
    db_session.add(logement)
    db_session.commit()

    assert repr(logement) == f"<Logement {logement.id_logement} {logement.adresse}>"