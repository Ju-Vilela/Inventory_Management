document.addEventListener("DOMContentLoaded", () => {
    const body = document.body;
    const toggleBtn = document.getElementById("themeToggle") || document.querySelector("button[onclick='toggleTheme()']");
    const icon = toggleBtn?.querySelector("i");

    // 🧠 Recuperar o tema salvo
    const savedTheme = localStorage.getItem("theme");

    if (savedTheme === "dark") {
        body.classList.add("dark");
        body.classList.remove("light");
        icon?.classList.remove("bi-brightness-high-fill");
        icon?.classList.add("bi-moon-stars");
    } else {
        body.classList.add("light");
        body.classList.remove("dark");
        icon?.classList.remove("bi-moon-stars");
        icon?.classList.add("bi-brightness-high-fill");
    }

    // 🌗 Alternar tema
    if (toggleBtn) {
        toggleBtn.addEventListener("click", () => {
            body.classList.toggle("dark");
            body.classList.toggle("light");

            if (body.classList.contains("dark")) {
                icon?.classList.remove("bi-brightness-high-fill");
                icon?.classList.add("bi-moon-stars");
                localStorage.setItem("theme", "dark");
            } else {
                icon?.classList.remove("bi-moon-stars");
                icon?.classList.add("bi-brightness-high-fill");
                localStorage.setItem("theme", "light");
            }
        });
    }
});
