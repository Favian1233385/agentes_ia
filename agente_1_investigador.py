from typing import List
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from config import config

# ==========================================
# 1. ESQUEMA DE DATOS ESTRUCTURADOS (Pydantic)
# ==========================================

class Lead(BaseModel):
    nombre_negocio: str = Field(description="Nombre comercial del negocio local")
    canton: str = Field(description="Cantón o ciudad donde opera")
    categoria: str = Field(description="Categoría o nicho comercial")
    problema_detectado: str = Field(description="Cuello de botella operativo en su atención o gestión")
    contacto: str = Field(description="Número de WhatsApp o correo electrónico de contacto")

class ListaLeads(BaseModel):
    leads: List[Lead] = Field(description="Lista de potenciales clientes detectados")

# ==========================================
# 2. INICIALIZACIÓN DEL MODELO GEMINI
# ==========================================

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3,
    google_api_key=config.GOOGLE_API_KEY
)

# Forzamos la salida estructurada según nuestro modelo Pydantic
agente_investigador_llm = llm.with_structured_output(ListaLeads)

# ==========================================
# 3. LÓGICA DEL AGENTE INVESTIGADOR
# ==========================================

def ejecutar_agente_1(nicho: str, provincia_canton: str, limite: int = 2) -> ListaLeads:
    prompt = f"""
    Actúa como un Investigador Comercial experto en negocios locales.
    Analiza el nicho de '{nicho}' en la zona de '{provincia_canton}'.
    
    Identifica {limite} perfiles de negocios locales que típicamente presenten los siguientes problemas:
    - Retrasos en responder WhatsApp a clientes a deshoras.
    - Falta de automatización en cotizaciones o catálogo de servicios.
    - Gestión manual de pedidos o reservas.
    
    Devuelve los datos estrictamente bajo la estructura requerida.
    """
    
    resultado = agente_investigador_llm.invoke(prompt)
    return resultado

if __name__ == "__main__":
    print("--- EJECUTANDO AGENTE 1: INVESTIGADOR DE MERCADO (GEMINI) ---")
    
    resultado_investigacion = ejecutar_agente_1(
        nicho="Hosterías y Turismo Ecológico", 
        provincia_canton="Tena, Napo"
    )
    
    print(f"\nSe encontraron {len(resultado_investigacion.leads)} oportunidades de negocio:\n")
    for idx, lead in enumerate(resultado_investigacion.leads, 1):
        print(f"[{idx}] {lead.nombre_negocio} ({lead.canton})")
        print(f"    Categoría: {lead.categoria}")
        print(f"    Problema: {lead.problema_detectado}")
        print(f"    Contacto: {lead.contacto}\n")