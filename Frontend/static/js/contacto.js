function actualizar_contador(){
    const mensaje = document.getElementById("mensaje")
    const contador = document.getElementById("contador")

    mensaje.addEventListener("input", function() {
        contador.textContent = `${mensaje.value.length}/500`
    })
}

function pausar_boton_envio(){
    const formulario = document.querySelector(".form")
    const boton = document.getElementById("boton-enviar")

    formulario.addEventListener("submit", function() {
        boton.disabled = true
        boton.textContent = "Enviando Mensaje"
    })
}

actualizar_contador()
pausar_boton_envio()




