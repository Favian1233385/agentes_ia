from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from config import config
from agente_1_investigador import Lead

# ==========================================
# 1. ESQUEMA DE DATOS ESTRUCTURADOS (Pydantic)
# ==========================================

class PropuestaEstrategica(BaseModel):
    nombre_negocio: str = Field(description="Nombre del negocio evaluado")
    diagnostico_clave: str = Field(description="Resumen ejecutivo del problema detectado")
    solucion_propuesta: str = Field(description="Descripción técnica/funcional de la solución")
    mensaje_pitch_whatsapp: str = Field(description="Mensaje directo y persuasivo listo para enviar por WhatsApp")

# ==========================================
# 2. LÓGICA DEL AGENTE ESTRATEGA
# ==========================================

def ejecutar_agente_2(
    lead: Lead, 
    nombre_desarrollador: str = config.DESARROLLADOR_NOMBRE,
    nombre_agencia: str = config.AGENCIA_NOMBRE
) -> PropuestaEstrategica:
    """
    Agente 2: Genera un diagnóstico comercial, propuesta técnica y script de ventas
    estructurado en Pydantic utilizando gemini-3.6-flash.
    """
    # Inicialización limpia sin temperature para evitar UserWarnings
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=config.obtener_siguiente_key()
    )

    # Forzamos la salida estructurada de manera estricta
    agente_estratega_llm = llm.with_structured_output(PropuestaEstrategica, method="json_schema")

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
    2. Diseña una propuesta de solución de software/automatización concreta.
    3. Escribe un mensaje corto, profesional y empático listo para enviar al dueño del negocio.
       REGLA OBLIGATORIA: El mensaje DEBE comenzar EXACTAMENTE con el saludo:
       "Hola, soy {nombre_desarrollador} de {nombre_agencia}."
    """
    
    try:
        return agente_estratega_llm.invoke(prompt)
    except Exception as e:
        print(f"❌ Error en Agente 2: {e}")
        return PropuestaEstrategica(
            nombre_negocio=lead.nombre_negocio,
            diagnostico_clave="No se pudo procesar el diagnóstico automatizado.",
            solucion_propuesta="Automatización comercial personalizada mediante chatbot y CRM.",
            mensaje_pitch_whatsapp=f"Hola, soy {nombre_desarrollador} de {nombre_agencia}. Me gustaría conversar sobre soluciones de automatización para {lead.nombre_negocio}."
        )