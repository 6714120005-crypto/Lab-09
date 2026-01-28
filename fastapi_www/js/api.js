<!DOCTYPE html>
<html lang="th">
    <head>
    <meta charset="UTF-8">
    <title>FastAPI Auth SPA</title>
</head>
<body>

<h1>🔐 FastAPI Auth</h1>

<nav>
    <button onclick="showPage('home')">Home</button>
    <button onclick="showPage('login')">Login</button>
    <button onclick="showPage('register')">Register</button>
    <button onclick="showPage('tools')">Tools</button>
</nav>

<section id="home" class="page">Home page</section>

<section id="login" class="page">
    <h2>Login</h2>
    <input id="loginEmail"><br>
        <input id="loginPassword" type="password"><br>
            <button onclick="login()">Login</button>
            <pre id="loginResponse"></pre>
</section>

<section id="register" class="page">
    <h2>Register</h2>
    <input id="regEmail"><br>
        <input id="regUsername"><br>
            <input id="regPassword" type="password"><br>
                <button onclick="register()">Register</button>
                <pre id="registerResponse"></pre>
</section>

<section id="tools" class="page">
    <h2>Tools</h2>
    <button onclick="getProfile()">Get Profile</button>
    <button onclick="logout()">Logout</button>
    <pre id="toolsResponse"></pre>
</section>

<!-- ✅ ต้องอยู่ท้าย body -->
<script src="js/app.js"></script>
</body>
</html>
