/**
 * Active la recherche dynamique sur un tableau HTML.
 * @param {string} inputId - L'ID du champ de recherche (input text).
 * @param {string} tableId - L'ID du tableau à filtrer.
 */
function setupTableSearch(inputId, tableId) {
    const input = document.getElementById(inputId);
    const table = document.getElementById(tableId);

    if (!input || !table) return;

    let timeout = null;

    input.addEventListener('keyup', function () {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            const filter = input.value.toLowerCase();
            const rows = table.querySelectorAll('tbody tr');

            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(filter) ? '' : 'none';
            });
        }, 200); // On attend 200ms de pause avant de filtrer
    });
}
