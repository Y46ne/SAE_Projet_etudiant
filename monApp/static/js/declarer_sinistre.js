document.addEventListener('DOMContentLoaded', function() {
    const residenceSelect = document.getElementById('filter-residence');
    const pieceSelect = document.getElementById('filter-piece');
    const rows = document.querySelectorAll('#biens-tbody tr');
    const totalDisplay = document.getElementById('total-indemnisation');
    const checkboxes = document.querySelectorAll('.checkbox-bien');
    const etatSelects = document.querySelectorAll('.etat-select');
    const summarySection = document.getElementById('summary-section');
    const summaryTbody = document.getElementById('summary-tbody');
    let isDirty = false;

    // Accessibilité RGAA
    // On ajoute aria-live pour que les changements de total soient annoncés
    if (totalDisplay) {
        totalDisplay.setAttribute('aria-live', 'polite');
    }

    const form = document.querySelector('.sinistre-form');
    if(form){
        form.addEventListener('change', () => isDirty = true);
        form.addEventListener('submit', () => isDirty = false);
    }
    window.addEventListener('beforeunload', (e) => {
        if (isDirty) {
            e.preventDefault();
            e.returnValue = "Attention, données non sauvegardées.";
        }
    });


    // Fonction déclenchée uniquement quand on change de Logement
    function onLogementChange() {
        const selectedLogementId = residenceSelect.value;

        // On décoche tout car on change de maison
        checkboxes.forEach(cb => {
            cb.checked = false;
        });

        pieceSelect.value = ""; 
        pieceSelect.disabled = false;
        Array.from(pieceSelect.options).forEach(opt => {
            if (opt.value === "") return;
            if (opt.dataset.logement === selectedLogementId) {
                opt.hidden = false;
            } else {
                opt.hidden = true;
            }
        });
        applyFilters();
    }

    // Fonction qui gère l'affichage
    function applyFilters() {
        const residenceId = residenceSelect.value;
        const pieceId = pieceSelect.value;

        rows.forEach(row => {
            const rowResidence = row.dataset.residence;
            const rowPiece = row.dataset.piece;
            
            let show = false;

            // On affiche seulement si c'est le bon logement
            if (residenceId && rowResidence === residenceId) {
                // Et si c'est la bonne pièce (ou toutes les pièces)
                if (pieceId === "" || rowPiece === pieceId) {
                    show = true;
                }
            }

            row.style.display = show ? '' : 'none';

        });

        calculateTotal();
    }

    // 3. Calcul financier
    function calculateTotal() {
        let total = 0;
        let summaryHTML = '';
        let hasChecked = false;
        const currentLogementId = residenceSelect.value;

        checkboxes.forEach(checkbox => {
            const row = checkbox.closest('tr');

            if (checkbox.checked && row.dataset.residence === currentLogementId) {
                hasChecked = true;
                
                const valeur = parseFloat(checkbox.dataset.valeur) || 0;
                const etatSelect = row.querySelector('.etat-select');
                const etat = etatSelect.value;
                const indemnisation = (etat === 'perte_totale') ? valeur : valeur * 0.5;
                
                total += indemnisation;

                summaryHTML += `<tr>
                    <td>${row.cells[1].textContent}</td>
                    <td>${row.cells[2].textContent}</td>
                    <td>${etatSelect.options[etatSelect.selectedIndex].text}</td>
                    <td>${indemnisation.toFixed(2)}€</td>
                </tr>`;
            }
        });
        summaryTbody.innerHTML = summaryHTML;
        summarySection.style.display = hasChecked ? 'block' : 'none';
        totalDisplay.textContent = total.toFixed(2) + '€';
    }

    residenceSelect.addEventListener('change', onLogementChange);
    pieceSelect.addEventListener('change', applyFilters);
    checkboxes.forEach(cb => cb.addEventListener('change', calculateTotal));
    etatSelects.forEach(select => select.addEventListener('change', calculateTotal));

    if (residenceSelect.value === "") {
        pieceSelect.disabled = true;
        rows.forEach(r => r.style.display = 'none');
    } else {
        pieceSelect.disabled = false;
        applyFilters(); 
    }
});