function actualizar_contador(){
    const mensaje = document.getElementById("mensaje")
    const contador = document.getElementById("contador")

    mensaje.addEventListener("input", function() {
        contador.textContent = `${mensaje.value.length}/500`
    })
}

actualizar_contador()





