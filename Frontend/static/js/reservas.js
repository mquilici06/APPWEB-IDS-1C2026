document.getElementById("notas").addEventListener("input", function () {
    document.getElementById("contador-notas").textContent = this.value.length + " / 300";
});
 
const hoy = new Date().toISOString().split("T")[0];
document.getElementById("fecha_reserva").min = hoy;