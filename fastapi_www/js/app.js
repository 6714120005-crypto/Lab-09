const API_BASE = "http://localhost:8000";

/* ===== PAGE ===== */
window.showPage = function (id) {
    document.querySelectorAll(".page").forEach(p => p.style.display = "none");
    document.getElementById(id).style.display = "block";
};

showPage("home");

/* ===== TOKEN ===== */
function setToken(data) {
    localStorage.setItem("access", data.access_token);
}

function token() {
    return localStorage.getItem("access");
}

/* ===== AUTH ===== */
window.login = async function () {
    const res = await fetch(API_BASE + "/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            email: loginEmail.value,
            password: loginPassword.value
        })
    });

    const data = await res.json();
    setToken(data);
    loginResponse.textContent = JSON.stringify(data, null, 2);
    showPage("tools");
};

window.register = async function () {
    const res = await fetch(API_BASE + "/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            email: regEmail.value,
            username: regUsername.value,
            password: regPassword.value
        })
    });

    registerResponse.textContent = JSON.stringify(await res.json(), null, 2);
};

/* ===== TOOLS ===== */
window.getProfile = async function () {
    const res = await fetch(API_BASE + "/users/me", {
        headers: {
            Authorization: "Bearer " + token()
        }
    });

    toolsResponse.textContent = JSON.stringify(await res.json(), null, 2);
};

window.logout = function () {
    localStorage.clear();
    toolsResponse.textContent = "Logged out";
    showPage("home");
};
