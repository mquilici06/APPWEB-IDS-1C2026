function aviso_fijo() {
    const aviso = document.querySelector(".aviso-fijo");
    if (aviso != null) {
        setTimeout(() => {
            aviso.style.display = "none";
        }, 3000);
    }
}

function actualizar_contador(){
    const mensaje = document.getElementById("mensaje");
    const contador = document.querySelector(".contador");

    mensaje.addEventListener("input", function() {
        contador.textContent = `${mensaje.value.length}/500`
    });
}

actualizar_contador();
aviso_fijo();