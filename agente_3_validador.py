import re
import dns.resolver
import phonenumbers
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from config import config

# ==========================================
# 1. ESQUEMAS DE DATOS ESTRUCTURADOS
# ==========================================

class ClasificacionPrioridad(BaseModel):
    prioridad: str = Field(description="Prioridad comercial evaluada: 'Alta', 'Media' o 'Baja'.")

class LeadValidado(BaseModel):
    contacto_limpio: str = Field(description="Número en formato E.164 (+593...) o correo validado.")
    tipo_contacto: str = Field(description="Clasificación: 'WhatsApp', 'Email' o 'Desconocido'.")
    prioridad: str = Field(description="Prioridad comercial: 'Alta', 'Media' o 'Baja'.")
    es_contacto_valido: bool = Field(description="True si superó las pruebas técnicas y es contactable.")
    motivo_rechazo: str = Field(default="", description="Razón técnica si el contacto fue rechazado.")

# ==========================================
# 2. FUNCIONES DE VALIDACIÓN TÉCNICA
# ==========================================

def validar_y_formatear_telefono(numero_raw: str, pais_default: str = "EC") -> tuple[bool, str]:
    try:
        limpio = re.sub(r"[^\d+]", "", numero_raw)
        parsed = phonenumbers.parse(limpio, pais_default)
        if phonenumbers.is_valid_number(parsed):
            return True, phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        return False, numero_raw
    except Exception:
        return False, numero_raw

def validar_dominio_email_mx(email_raw: str) -> tuple[bool, str]:
    match = re.match(r"^[\w\.-]+@([\w\.-]+\.\w+)$", email_raw.strip().lower())
    if not match:
        return False, "Sintaxis de e-mail inválida."
    
    dominio = match.group(1)
    try:
        registros_mx = dns.resolver.resolve(dominio, 'MX')
        if len(registros_mx) > 0:
            return True, email_raw.strip().lower()
        return False, f"El dominio {dominio} no tiene servidores MX activos."
    except Exception as e:
        return False, f"Error al verificar dominio {dominio}: {str(e)}"

# ==========================================
# 3. LÓGICA DEL AGENTE VALIDADOR
# ==========================================

def ejecutar_agente_3(contacto_raw: str, problema: str, pais_codigo: str = "EC") -> LeadValidado:
    contacto_limpio = contacto_raw.strip()
    tipo_contacto = "Desconocido"
    es_valido = False
    motivo = ""

    # Validaciones técnicas deterministas
    if "@" in contacto_limpio:
        tipo_contacto = "Email"
        es_valido, resultado_email = validar_dominio_email_mx(contacto_limpio)
        if es_valido:
            contacto_limpio = resultado_email
        else:
            motivo = resultado_email
    else:
        es_valido, resultado_telefono = validar_y_formatear_telefono(contacto_limpio, pais_codigo)
        if es_valido:
            tipo_contacto = "WhatsApp"
            contacto_limpio = resultado_telefono
        else:
            motivo = "Número telefónico no válido o estructura incorrecta."

    # Si la validación de formato falla, finaliza temprano sin gastar tokens de IA
    if not es_valido:
        return LeadValidado(
            contacto_limpio=contacto_raw,
            tipo_contacto=tipo_contacto,
            prioridad="Baja",
            es_contacto_valido=False,
            motivo_rechazo=motivo
        )

    # Evaluación de Prioridad mediante LLM
    llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=config.obtener_siguiente_key()
    ).with_structured_output(ClasificacionPrioridad)

    prompt_prioridad = f"""
    Actúa como un Analista de Inteligencia Comercial B2B.
    Analiza la criticidad de la siguiente oportunidad:
    - Contacto: {contacto_limpio} ({tipo_contacto})
    - Problema Detectado: {problema}

    Determina la Prioridad comercial ('Alta', 'Media', 'Baja'):
    - 'Alta': El problema implica pérdida directa de clientes o ventas inmediatas.
    - 'Media': El problema afecta la eficiencia o reputación.
    - 'Baja': Problema menor o genérico.
    """
    
    try:
        resultado = llm.invoke(prompt_prioridad)
        prioridad_calculada = resultado.prioridad if resultado.prioridad in ["Alta", "Media", "Baja"] else "Media"
    except Exception:
        prioridad_calculada = "Media"

    return LeadValidado(
        contacto_limpio=contacto_limpio,
        tipo_contacto=tipo_contacto,
        prioridad=prioridad_calculada,
        es_contacto_valido=True,
        motivo_rechazo=""
    )