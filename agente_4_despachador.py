import urllib.parse
from pydantic import BaseModel, Field

# ==========================================
# 1. ESQUEMA DE SALIDA DEL AGENTE 4 (MULTICANAL)
# ==========================================

class DespachoContacto(BaseModel):
    contacto_destino: str = Field(description="Número de teléfono o dirección de correo electrónico")
    tipo_canal: str = Field(description="Canal de comunicación ('WhatsApp' o 'Email')")
    mensaje_codificado: str = Field(description="Texto del mensaje codificado para URL")
    url_despacho: str = Field(description="Enlace directo listo para ejecutar (wa.me o mailto:)")
    # Campo retrocompatible con app.py actual
    url_directa_wa: str = Field(default="", description="Alias retrocompatible para la URL de despacho")
    estado_despacho: str = Field(description="Estado de la preparación del envío ('Listo para envío', 'Contacto no válido')")


# ==========================================
# 2. LÓGICA DEL AGENTE DESPACHADOR
# ==========================================

def ejecutar_agente_4(contacto: str, mensaje: str, tipo_contacto: str = "WhatsApp", negocio: str = "su negocio") -> DespachoContacto:
    """
    Genera la URL de envío directo para WhatsApp o Email codificando adecuadamente los parámetros.
    """
    # --------------------------------------------------
    # CANAL 1: CORREO ELECTRÓNICO (EMAIL)
    # --------------------------------------------------
    if tipo_contacto == "Email":
        contacto_email = contacto.strip()
        
        # Validación básica de estructura de correo
        if not contacto_email or "@" not in contacto_email:
            return DespachoContacto(
                contacto_destino=contacto,
                tipo_canal="Email",
                mensaje_codificado="",
                url_despacho="",
                url_directa_wa="",
                estado_despacho="Correo no válido"
            )
        
        # Codificación URL del mensaje y asunto
        asunto = f"Propuesta de mejora tecnológica para {negocio}"
        asunto_url = urllib.parse.quote(asunto)
        mensaje_url = urllib.parse.quote(mensaje)
        
        # Construcción del protocolo mailto:
        url_mailto = f"mailto:{contacto_email}?subject={asunto_url}&body={mensaje_url}"
        
        return DespachoContacto(
            contacto_destino=contacto_email,
            tipo_canal="Email",
            mensaje_codificado=mensaje_url,
            url_despacho=url_mailto,
            url_directa_wa=url_mailto,  # Mantener retrocompatibilidad
            estado_despacho="Listo para envío"
        )

    # --------------------------------------------------
    # CANAL 2: WHATSAPP (LÓGICA ORIGINAL PRESERVADA)
    # --------------------------------------------------
    else:
        # Eliminar caracteres no numéricos excepto el '+'
        numero_limpio = "".join(c for c in contacto if c.isdigit() or c == "+")
        
        # Quitar el '+' para la API wa.me
        if numero_limpio.startswith("+"):
            numero_wa = numero_limpio[1:]
        else:
            numero_wa = numero_limpio

        if not numero_wa or len(numero_wa) < 8:
            return DespachoContacto(
                contacto_destino=contacto,
                tipo_canal="WhatsApp",
                mensaje_codificado="",
                url_despacho="",
                url_directa_wa="",
                estado_despacho="Número no válido"
            )

        # Codificar el texto del mensaje para URL
        mensaje_url = urllib.parse.quote(mensaje)
        
        # Construir enlace directo Click-to-Chat de WhatsApp
        url_wa = f"https://wa.me/{numero_wa}?text={mensaje_url}"

        return DespachoContacto(
            contacto_destino=numero_wa,
            tipo_canal="WhatsApp",
            mensaje_codificado=mensaje_url,
            url_despacho=url_wa,
            url_directa_wa=url_wa,  # Mantener retrocompatibilidad
            estado_despacho="Listo para envío"
        )


if __name__ == "__main__":
    print("--- PRUEBA AGENTE 4: DESPACHADOR MULTICANAL ---")
    
    # Prueba 1: WhatsApp
    tel = "+593987654321"
    msg_wa = "Hola, vi tu local y tengo una propuesta para automatizar tus ventas por WhatsApp."
    res_wa = ejecutar_agente_4(tel, msg_wa, tipo_contacto="WhatsApp", negocio="Ferretería Central")
    print(f"\n[WhatsApp] Estado: {res_wa.estado_despacho}")
    print(f"[WhatsApp] URL: {res_wa.url_despacho}")

    # Prueba 2: Email
    mail = "contacto@ferreteria.com"
    msg_mail = "Estimado equipo, adjunto propuesta de optimización de procesos."
    res_mail = ejecutar_agente_4(mail, msg_mail, tipo_contacto="Email", negocio="Ferretería Central")
    print(f"\n[Email] Estado: {res_mail.estado_despacho}")
    print(f"[Email] URL: {res_mail.url_despacho}")