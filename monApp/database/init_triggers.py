from ..app import db

def create_sinistre_montant_triggers():
    """Crée les triggers pour mettre à jour automatiquement le montant_estime dans sinistre."""

    trigger_insert = """
    CREATE TRIGGER IF NOT EXISTS update_sinistre_montant_after_insert_impacte
    AFTER INSERT ON impacte
    FOR EACH ROW
    BEGIN
        UPDATE sinistre
        SET montant_estime = (
            SELECT COALESCE(SUM(degat_estime), 0)
            FROM impacte
            WHERE id_sinistre = NEW.id_sinistre
        )
        WHERE id_sinistre = NEW.id_sinistre;
    END;
    """

    trigger_update = """
    CREATE TRIGGER IF NOT EXISTS update_sinistre_montant_after_update_impacte
    AFTER UPDATE OF degat_estime ON impacte
    FOR EACH ROW
    BEGIN
        UPDATE sinistre
        SET montant_estime = (
            SELECT COALESCE(SUM(degat_estime), 0)
            FROM impacte
            WHERE id_sinistre = NEW.id_sinistre
        )
        WHERE id_sinistre = NEW.id_sinistre;
    END;
    """

    trigger_delete = """
    CREATE TRIGGER IF NOT EXISTS update_sinistre_montant_after_delete_impacte
    AFTER DELETE ON impacte
    FOR EACH ROW
    BEGIN
        UPDATE sinistre
        SET montant_estime = (
            SELECT COALESCE(SUM(degat_estime), 0)
            FROM impacte
            WHERE id_sinistre = OLD.id_sinistre
        )
        WHERE id_sinistre = OLD.id_sinistre;
    END;
    """

    with db.engine.connect() as connection:
        with connection.begin():
            connection.execute(db.text(trigger_insert))
            connection.execute(db.text(trigger_update))
            connection.execute(db.text(trigger_delete))

    print("✅ Triggers pour la mise à jour du montant_estime créés ou mis à jour.")
