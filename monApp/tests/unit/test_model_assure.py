from monApp.database import Assure, Assureur, User
import datetime


def test_assure_repr(db_session):
    # Assure.email references User.Login and Assure requires an Assureur
    user = User(Login="cricri@dal.com", Password="pwd")
    db_session.add(user)

    assureur = Assureur(
        nom="Test",
        prenom="Assureur",
        email="test@assureur.com",
        mot_de_passe="secret",
        telephone="0123456789",
        societe="TestAssur"
    )
    db_session.add(assureur)
    db_session.commit()

    assure = Assure(
        nom="DAL",
        prenom="Cricri",
        date_naissance=datetime.datetime(1990, 1, 1),
        email=user.Login,
        mdp_assure="mdp",
        telephone="0123456789",
        id_assureur=assureur.id_assureur
    )
    db_session.add(assure)
    db_session.commit()

    assert repr(assure) == f"<Assure {assure.id_assure} {assure.prenom} {assure.nom}>"
