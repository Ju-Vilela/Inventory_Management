let confirmActionUrl = ''; // guarda a URL temporariamente

function showConfirmModal(message, actionUrl) {
    const modalMessage = document.getElementById("confirmModalMessage");
    modalMessage.textContent = message;
    confirmActionUrl = actionUrl;

    const myModal = new bootstrap.Modal(document.getElementById('confirmGlobalModal'));
    myModal.show();
}

// Quando o botão for clicado, aí sim o form é enviado com a URL correta
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById("confirmModalForm");
    form.addEventListener("submit", function (e) {
        // Garante que o form só vai pra URL quando o botão for clicado
        form.action = confirmActionUrl;
    });
});

// Script para esconder o alerta após 5 segundos
document.addEventListener('DOMContentLoaded', function () {
    const alert = document.getElementById('#alert-container');
    if (alert) {
        setTimeout(function () {
            if (alert) {
                alert.classList.remove('show');
                alert.classList.add('fade');
                setTimeout(() => alert.remove(), 500); // espera o fade terminar e remove
            }
        }, 5000);
    }
});
