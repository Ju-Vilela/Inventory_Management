document.addEventListener("DOMContentLoaded", function () {
    const buscaProduto = document.getElementById('buscaProdutos');
    const tabelaProduto = document.getElementById('produtoTabela');

    buscaProduto.addEventListener('input', function () {
        const searchTerm = buscaProduto.value.toLowerCase();
        const rows = tabelaProduto.getElementsByTagName('tr');

        Array.from(rows).forEach(function (row) {
            const item = row.cells[0].textContent.toLowerCase();
            const categoria = row.cells[1].textContent.toLowerCase();
            const marca = row.cells[2].textContent.toLowerCase();

            if (item.includes(searchTerm) || categoria.includes(searchTerm) || marca.includes(searchTerm)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    });

    document.querySelectorAll(".clickable-row").forEach(row => {
        row.addEventListener("click", () => {
            window.location.href = row.dataset.href;
        });
    });

    const sortDirections = {}; // isso vai salvar o estado de cada coluna!

    const tbody = document.querySelector("#produtoTabela");
    const rows = Array.from(tbody.querySelectorAll("tr"));
    const validadeProxima = 30;

    rows.sort((a, b) => {
        const validadeA = new Date(a.dataset.validade);
        const validadeB = new Date(b.dataset.validade);
        const diasA = (validadeA - new Date()) / (1000 * 60 * 60 * 24);
        const diasB = (validadeB - new Date()) / (1000 * 60 * 60 * 24);

        if (diasA < validadeProxima && diasB >= validadeProxima) {
            return -1;
        } else if (diasA >= validadeProxima && diasB < validadeProxima) {
            return 1;
        } else {
            return diasA - diasB;
        }
    });

    rows.forEach(row => tbody.appendChild(row));

    const ths = document.querySelectorAll('th[data-column]');
    ths.forEach(th => {
        th.addEventListener('click', function () {
            const index = Array.from(ths).indexOf(th);
            const rows = Array.from(tbody.rows);

            // alterna direção
            sortDirections[index] = !sortDirections[index]; // inverte o valor true/false
            const ascending = sortDirections[index];

            // remove classes antigas
            ths.forEach(header => header.classList.remove('ascending', 'descending'));
            th.classList.add(ascending ? 'ascending' : 'descending');

            rows.sort((a, b) => {
                const normalize = str => str.trim().toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");

                let compareA = a.cells[index].textContent.trim();
                let compareB = b.cells[index].textContent.trim();

                // Se for a coluna de validade, faz a mágica de transformar em datas
                if (th.dataset.column === 'validade') {
                    const [diaA, mesA, anoA] = compareA.split('/');
                    const [diaB, mesB, anoB] = compareB.split('/');

                    compareA = new Date(`${anoA}-${mesA}-${diaA}`);
                    compareB = new Date(`${anoB}-${mesB}-${diaB}`);
                } else {
                    compareA = compareA.toLowerCase();
                    compareB = compareB.toLowerCase();
                }

                if (compareA < compareB) return ascending ? -1 : 1;
                if (compareA > compareB) return ascending ? 1 : -1;
                return 0;
            });

            // reanexa os rows ordenados
            rows.forEach(row => tbody.appendChild(row));
        });
    });

});
