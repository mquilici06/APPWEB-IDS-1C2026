import os
from urllib.parse import quote
from flask import jsonify
from flask_mail import Message
import qrcode
import io

def errores(codigo,mensaje,descripcion):
    return jsonify({
        "errors": [
            {
                "code": codigo,
                "message": mensaje,
                "description": descripcion,
                "level": "error"
            }
        ]
    }), codigo


def generar_qr(datos: str) -> bytes:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=4,
    )
    qr.add_data(datos)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#6d071a", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def enviar_mail_reserva(mail, nombre, email, fecha, hora, personas, id_reserva, notas=""):
    qr_texto = (
        f"----ALTEZZA RISTORANTE----\n"
        f"Reserva #{id_reserva}\n"
        f"Nombre: {nombre}\n"
        f"Fecha: {fecha}\n"
        f"Hora: {hora}\n"
        f"Personas: {personas}"
    )
    qr_texto += f"\nNotas: {notas}" if notas else "\nSin notas adicionales"

    qr_bytes = generar_qr(qr_texto)

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5001")
    link_cancelar = f"{frontend_url}/reservas/cancelar/{id_reserva}?email={quote(email)}"

    mensaje = Message(
        subject=f"Tu reserva en Altezza - #{id_reserva}",
        sender="altezzaadmin@gmail.com",
        recipients=[email],
    )
    mensaje.body = (
        f"Hola {nombre},\n\n"
        f"Tu reserva fue confirmada con éxito.\n\n"
        f"  Reserva N°: {id_reserva}\n"
        f"  Fecha: {fecha}\n"
        f"  Hora: {hora}\n"
        f"  Personas: {personas}\n"
        + (f"  Notas: {notas}\n" if notas else "")
        + f"\nPresentá el QR adjunto al llegar al restaurante.\n\n"
        f"Si necesitás cancelar tu reserva, entrá a este link:\n{link_cancelar}\n\n"
        f"¡Te esperamos!\n"
        f"Altezza Ristorante · Av. Del Libertador 6820, CABA"
    )
    mensaje.html = f"""
    <div style="font-family: Arial, sans-serif; color: #333; max-width: 500px; margin: 0 auto;">
        <h2 style="color: #6d071a;">¡Hola {nombre}!</h2>
        <p>Tu reserva fue confirmada con éxito.</p>
        <table style="margin: 16px 0;">
            <tr><td><strong>Reserva N°:</strong></td><td>{id_reserva}</td></tr>
            <tr><td><strong>Fecha:</strong></td><td>{fecha}</td></tr>
            <tr><td><strong>Hora:</strong></td><td>{hora}</td></tr>
            <tr><td><strong>Personas:</strong></td><td>{personas}</td></tr>
            {f"<tr><td><strong>Notas:</strong></td><td>{notas}</td></tr>" if notas else ""}
        </table>
        <p>Presentá el QR adjunto al llegar al restaurante.</p>
        <p>¿No podés venir?</p>
        <a href="{link_cancelar}"
           style="display:inline-block; background-color:#6d071a; color:white; text-decoration:none;
                  padding:12px 24px; border-radius:4px; font-weight:bold; margin: 10px 0;">
            Cancelar reserva
        </a>
        <p style="margin-top: 24px;">¡Te esperamos!<br>
        Altezza Ristorante · Av. Del Libertador 6820, CABA</p>
    </div>
    """
    mensaje.attach(
        filename=f"reserva_{id_reserva}_qr.png",
        content_type="image/png",
        data=qr_bytes,
        disposition="attachment",
    )
    mail.send(mensaje)