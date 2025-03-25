document.addEventListener("DOMContentLoaded", function () {
    let menuBtn = document.querySelector("#navigation .menu-btn");
    let app = document.querySelector("#app");

    menuBtn.addEventListener("click", function () {
        app.classList.toggle("active");
        menuBtn.classList.toggle("active");
    });
});