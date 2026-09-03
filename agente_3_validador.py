import re
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from config import config

# ==========================================
# 1. ESQUEMA DE SALIDA DEL AGENTE 3
# ==========================================

class LeadValidado(BaseModel):
    contacto_limpio: str = Field(description="Número de teléfono en formato internacional o email formateado")
    tipo_contacto: str = Field(description="Clasificación: 'WhatsApp', 'Email' o 'Desconocido'")
    prioridad: str = Field(description="Calificación del lead: 'Alta', 'Media' o 'Baja'")
    es_contacto_valido: bool = Field(description="True si el contacto parece legítimo para enviar un mensaje")

# ==========================================
# 2. INICIALIZACIÓN DEL MODELO
# ==========================================

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.1,  # Temperatura baja para mayor precisión en la validación
    google_api_key=config.GOOGLE_API_KEY
)

agente_validador_llm = llm.with_structured_output(LeadValidado)

# ==========================================
# 3. LÓGICA DEL AGENTE VALIDADOR
# ==========================================

def ejecutar_agente_3(contacto_raw: str, problema: str) -> LeadValidado:
    """
    Valida, clasifica y normaliza los datos del contacto antes de procesar el envío.
    """
    prompt = f"""
    Actúa como un Especialista en Control de Calidad de Datos Comerciales para Ecuador.
    
    Analiza el siguiente contacto recibido: '{contacto_raw}'
    Y el problema asociado: '{problema}'
    
    Reglas de negocio:
    1. Si es un número telefónico ecuatoriano (ej. 0987654321), asegúrate de convertirlo al formato internacional con prefijo '+593' (ej. +593987654321).
    2. Determina el tipo de contacto ('WhatsApp', 'Email' o 'Desconocido').
    3. Evalúa la prioridad ('Alta', 'Media', 'Baja') según la criticidad del problema del cliente.
    4. Marca 'es_contacto_valido' como True si tiene una estructura coherente para ser contactado.
    """
    
    resultado = agente_validador_llm.invoke(prompt)
    return resultado

if __name__ == "__main__":
    print("--- PRUEBA AGENTE 3: VALIDADOR DE DATOS ---")
    contacto_prueba = "0987654321"
    problema_prueba = "No responde WhatsApp fuera del horario comercial, pierde clientes."
    
    resultado = ejecutar_agente_3(contacto_prueba, problema_prueba)
    print(f"Contacto Original: {contacto_prueba}")
    print(f"Contacto Limpio: {resultado.contacto_limpio}")
    print(f"Tipo: {resultado.tipo_contacto}")
    print(f"Prioridad: {resultado.prioridad}")
    print(f"Válido: {resultado.es_contacto_valido}")