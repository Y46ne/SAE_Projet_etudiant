from monApp.database import Bien
import datetime
def test_bien_repr(db_session):
    bien = Bien(
        nom_bien="TestBien",
        description="Description",
        categorie="Catégorie",
        date_achat=datetime.datetime(2020, 1, 1),
        prix_achat=100.0,
        etat="Neuf",
        valeur_actuelle=90.0,
        id_piece=1,
    )
    db_session.add(bien)
    db_session.commit()

    assert repr(bien) == f"<Bien ({bien.id_bien}) {bien.nom_bien}>"

