function login() {
    fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            usuario: document.getElementById("usuario").value,
            senha: document.getElementById("senha").value
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.mensagem) {
            document.getElementById("login-area").style.display = "none";
            document.getElementById("ocorrencia-area").style.display = "block";
            listarOcorrencias();
        } else {
            document.getElementById("login-msg").innerText = data.erro;
        }
    });
}

function criarOcorrencia() {
    fetch("/ocorrencias", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            titulo: document.getElementById("titulo").value,
            descricao: document.getElementById("descricao").value,
            prioridade: document.getElementById("prioridade").value
        })
    })
    .then(res => res.json())
    .then(() => {
        document.getElementById("titulo").value = "";
        document.getElementById("descricao").value = "";
        listarOcorrencias();
    });
}

function listarOcorrencias() {
    fetch("/ocorrencias")
        .then(res => res.json())
        .then(dados => {
            const tbody = document.getElementById("lista");
            tbody.innerHTML = "";

            dados.forEach(o => {
                const tr = document.createElement("tr");

                tr.innerHTML = `
                    <td>${o[0]}</td>
                    <td>${o[1]}</td>
                    <td>${o[2]}</td>
                    <td>${o[3]}</td>
                    <td>${new Date(o[4]).toLocaleString()}</td>
                `;

                tbody.appendChild(tr);
            });
        });
}
