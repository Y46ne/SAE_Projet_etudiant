from flask import flash
from flask_login import current_user

def verifier_droit_logement(logement):
    """Vérifie si l'utilisateur connecté a accès au logement."""
    if current_user.assure_profile not in logement.assures:
        flash("Vous n'avez pas accès à ce logement.", "danger")
        return False
    return True

def verifier_droit_piece(piece):
    """Vérifie si l'utilisateur connecté a accès à la pièce (via le logement)."""
    user_logement_ids = [l.id_logement for l in current_user.assure_profile.logements]
    if piece.id_logement not in user_logement_ids:
        flash("Vous n'avez pas accès à cette pièce.", "danger")
        return False
    return True
