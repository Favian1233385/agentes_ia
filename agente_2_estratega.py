from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from config import config
from agente_1_investigador import Lead, ejecutar_agente_1

# ==========================================
# 1. ESQUEMA DE SALIDA DEL AGENTE 2
# ==========================================

class PropuestaEstrategica(BaseModel):
    nombre_negocio: str = Field(description="Nombre del negocio evaluado")
    diagnostico_clave: str = Field(description="Resumen ejecutivo del problema detectado")
    solucion_propuesta: str = Field(description="Descripción técnica/funcional de la solución (ej. Bot de WhatsApp, CRM, etc.)")
    mensaje_pitch_whatsapp: str = Field(description="Mensaje directo y persuasivo listo para enviar por WhatsApp al dueño")

# ==========================================
# 2. INICIALIZACIÓN DEL MODELO
# ==========================================

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.4,
    google_api_key=config.GOOGLE_API_KEY
)

agente_estratega_llm = llm.with_structured_output(PropuestaEstrategica)

# ==========================================
# 3. LÓGICA DEL AGENTE ESTRATEGA
# ==========================================

def ejecutar_agente_2(lead: Lead, nombre_desarrollador: str = config.DESARROLLADOR_NOMBRE,nombre_agencia: str = config.AGENCIA_NOMBRE) -> PropuestaEstrategica:
    prompt = f"""
    Actúa como un Consultor de Tecnología y Ventas B2B para negocios locales.
    Tu nombre/firma es: '{nombre_desarrollador}'.
    La agencia para la que trabajas es: '{nombre_agencia}'.
    
    Analiza el siguiente prospecto:
    - Negocio: {lead.nombre_negocio} ({lead.canton})
    - Categoría: {lead.categoria}
    - Problema Detectado: {lead.problema_detectado}
    
   Tu tarea:
    1. Elabora un diagnóstico breve del impacto negativo de su problema actual.
    2. Diseña una propuesta de solución de software/automatización concreta (ej. asistente de WhatsApp con IA, catálogo interactivo, etc.).
    3. Escribe un mensaje corto, profesional y empático listo para enviar al dueño del negocio. 
       REGLA OBLIGATORIA: El mensaje DEBE comenzar EXACTAMENTE con el siguiente saludo:
       "Hola, soy {nombre_desarrollador} de {nombre_agencia}." 
       Seguido de la propuesta personalizada según el negocio. NO utilices corchetes, variables vacías ni etiquetas como '[Tu Nombre]' o '[Tu Empresa]'.
    """
    
    resultado = agente_estratega_llm.invoke(prompt)
    return resultado

if __name__ == "__main__":
    print("--- INICIANDO FLUJO DE PRUEBA: AGENTE 1 + AGENTE 2 ---\n")
    
    investigacion = ejecutar_agente_1("Hosterías y Turismo Ecológico", "Tena, Napo")
    primer_lead = investigacion.leads[0]
    
    print(f"-> Analizando propuesta comercial para: {primer_lead.nombre_negocio}...")
    propuesta = ejecutar_agente_2(primer_lead)
    
    print("\n==============================================")
    print(f"PROPUESTA COMERCIAL - {propuesta.nombre_negocio}")
    print("==============================================")
    print(f"Diagnóstico: {propuesta.diagnostico_clave}\n")
    print(f"Solución Recomendada: {propuesta.solucion_propuesta}\n")
    print("Mensaje Pitch para WhatsApp:")
    print("----------------------------------------------")
    print(propuesta.mensaje_pitch_whatsapp)
    print("----------------------------------------------")