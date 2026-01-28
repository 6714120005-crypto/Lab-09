async function loadProfile() {
    requireAuth();
    const res = await fetch(API_URL + "/users/me", {
        headers: authHeader()
    });
    const data = await res.json();
    info.innerText = JSON.stringify(data, null, 2);
}

async function updateProfile() {
    await fetch(API_URL + "/users/me", {
        method: "PATCH",
        headers: authHeader(),
        body: JSON.stringify({username: newname.value})
    });
    alert("Updated");
}
