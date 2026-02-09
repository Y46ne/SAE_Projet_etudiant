document.addEventListener('DOMContentLoaded', function() {
        const logementSelect = document.getElementById('logement_id');
        const pieceSelect = document.getElementById('piece_id');
        
        const allPieceOptions = Array.from(pieceSelect.querySelectorAll('.piece-option'));

        function updatePiecesList() {
            const selectedLogementId = logementSelect.value;
            const currentPieceValue = pieceSelect.value; 

            pieceSelect.innerHTML = '<option value="" disabled selected>Sélectionner une pièce</option>';
            
            if (selectedLogementId) {
                pieceSelect.disabled = false;
                let isValueRestored = false;

                allPieceOptions.forEach(function(option) {
                    if (option.dataset.logementId === selectedLogementId) {
                        const newOption = option.cloneNode(true);
                        
                        if (newOption.value === currentPieceValue) {
                            newOption.selected = true;
                            isValueRestored = true;
                        }
                        
                        pieceSelect.appendChild(newOption);
                    }
                });

                if (isValueRestored) {
                    pieceSelect.value = currentPieceValue;
                }
            } else {
                pieceSelect.disabled = true;
            }
        }

        logementSelect.addEventListener('change', updatePiecesList);

        updatePiecesList();
    });