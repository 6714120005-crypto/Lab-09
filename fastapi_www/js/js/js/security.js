async function refresh() {
    const res = await fetch(API_URL + "/auth/refresh", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            refresh_token: localStorage.getItem("refresh_token")
        })
    });
    const data = await res.json();
    localStorage.setItem("access_token", data.access_token);
    alert("Token refreshed");
}

async function logoutAll() {
    await fetch(API_URL + "/auth/logout-all", {
        method: "POST",
        headers: authHeader()
    });
    logout();
}
