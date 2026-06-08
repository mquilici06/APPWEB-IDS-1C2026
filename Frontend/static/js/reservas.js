document.getElementById("fecha_reserva").addEventListener("input", function () {
    const dia = new Date(this.value + "T00:00:00").getDay();
    if (![0, 4, 5, 6].includes(dia)) {
        this.value = "";
        alert("Solo aceptamos reservas de jueves a domingo.");
    }
});


document.getElementById("notas").addEventListener("input", function () {
    document.getElementById("contador-notas").textContent = this.value.length + " / 300";
});
 
const hoy = new Date().toISOString().split("T")[0];
document.getElementById("fecha_reserva").min = hoy;