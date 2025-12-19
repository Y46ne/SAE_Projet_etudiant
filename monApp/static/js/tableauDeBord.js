function confirmerSuppression(logementId) {
    if (confirm('Êtes-vous sûr de vouloir supprimer ce logement ?')) {
        fetch(`{{ url_for('delete_logement', id=0) }}`.replace('0', logementId), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Erreur lors de la suppression');
            }
        });
    }
}
function afficherPlus() {
    window.location.href = "{{ url_for('mes_logements') }}";
}
