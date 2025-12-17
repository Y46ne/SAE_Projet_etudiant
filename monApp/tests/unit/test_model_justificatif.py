from monApp.database import Justificatif, Bien, Piece, Logement
from datetime import datetime, date

def test_justificatif_creation(db_session):
    # Création de la hiérarchie
    logement = Logement(nom_logement="L", adresse="A", type_logement="T", surface=10)
    db_session.add(logement)
    db_session.commit()
    
    piece = Piece(nom_piece="P", surface=10, id_logement=logement.id_logement)
    db_session.add(piece)
    db_session.commit()
    
    bien = Bien(nom_bien="B", categorie="C", date_achat=date.today(), prix_achat=10, id_piece=piece.id_piece)
    db_session.add(bien)
    db_session.commit()

    justificatif = Justificatif(
        chemin_fichier="uploads/facture.pdf",
        type_justificatif="Facture",
        # Correction : Utilisation d'un objet datetime, pas une string
        date_ajout=datetime.now(),
        id_bien=bien.id_bien
    )
    db_session.add(justificatif)
    db_session.commit()

    assert justificatif.id_justificatif is not None
    assert justificatif.type_justificatif == "Facture"
    assert isinstance(justificatif.date_ajout, datetime)