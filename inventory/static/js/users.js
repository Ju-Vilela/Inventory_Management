document.addEventListener("DOMContentLoaded", () => {
    const campoBusca = document.getElementById("buscaUsuarios");
    const linhas = document.querySelectorAll("#tabelaUsuarios tr");

    campoBusca?.addEventListener("input", () => {
        const termo = campoBusca.value.toLowerCase();
        linhas.forEach(linha => {
            const texto = linha.textContent.toLowerCase();
            linha.style.display = texto.includes(termo) ? "" : "none";
        });
    });
});
