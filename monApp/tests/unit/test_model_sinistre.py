from monApp.database import Sinistre, Logement, Assure, Assureur, User
import datetime


def test_sinistre_repr(db_session):
    # Create Logement and its owner
    user = User(Login="owner2", Password="p")
    db_session.add(user)
    assureur = Assureur(nom="AN", prenom="AP", email="aa@aa.com", mot_de_passe="m")
    db_session.add(assureur)
    db_session.commit()

    assure = Assure(nom="N", prenom="P", date_naissance=None, email=user.Login, mdp_assure="mdp", id_assureur=assureur.id_assureur)
    db_session.add(assure)
    db_session.commit()

    logement = Logement(adresse="Addr 3")
    logement.id_assure = assure.id_assure
    db_session.add(logement)
    db_session.commit()

    sinistre = Sinistre(
        date_sinistre=datetime.date(2020, 5, 17),
        type_sinistre="Sinistre de test",
        description="Description du sinistre",
        numero_sinistre="123456",
        id_logement=logement.id_logement,
    )
    db_session.add(sinistre)
    db_session.commit()

    assert repr(sinistre) == f"<Sinistre {sinistre.id_sinistre} {sinistre.numero_sinistre}>"