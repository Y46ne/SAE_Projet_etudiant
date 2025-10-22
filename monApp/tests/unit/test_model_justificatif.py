from monApp.database import Justificatif
def test_justificatif_repr(db_session):
    justificatif  = Justificatif(
        type_justificatif="Justificatif de test",
        chemin_fichier="chemin/vers/le/fichier.pdf",
        date_ajout="2023-01-01",
        id_bien=1
    )
    db_session.add(justificatif)
    db_session.commit()

    assert repr(justificatif) == f"<Justificatif ({justificatif.id_justificatif}) {justificatif.type_justificatif}>"
