document.addEventListener("DOMContentLoaded", () => {
    const body = document.body;
    const toggleBtn = document.getElementById("themeToggle") || document.querySelector("button[onclick='toggleTheme()']");
    const icon = toggleBtn?.querySelector("i");

    // 🧠 Recuperar o tema salvo
    const savedTheme = localStorage.getItem("theme");

    if (savedTheme === "dark") {
        body.classList.add("dark");
        body.classList.remove("light");
        icon?.classList.remove("fa-sun");
        icon?.classList.add("fa-moon");
    } else {
        body.classList.add("light");
        body.classList.remove("dark");
        icon?.classList.remove("fa-moon");
        icon?.classList.add("fa-sun");
    }

    // 🌗 Alternar tema
    if (toggleBtn) {
        toggleBtn.addEventListener("click", () => {
            body.classList.toggle("dark");
            body.classList.toggle("light");

            if (body.classList.contains("dark")) {
                icon?.classList.remove("fa-sun");
                icon?.classList.add("fa-moon");
                localStorage.setItem("theme", "dark");
            } else {
                icon?.classList.remove("fa-moon");
                icon?.classList.add("fa-sun");
                localStorage.setItem("theme", "light");
            }
        });
    }
});
