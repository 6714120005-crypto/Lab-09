async function hash() {
    const res = await fetch(API_URL + "/tools/bcrypt", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({password: pw.value})
    });
    out.innerText = await res.text();
}
