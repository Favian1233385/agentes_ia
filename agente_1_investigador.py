import time
from typing import List
from google import genai
from google.genai import types
from google.genai.errors import APIError
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from config import config

# ==========================================
# 1. ESQUEMA DE DATOS ESTRUCTURADOS (Pydantic)
# ==========================================

class Lead(BaseModel):
    nombre_negocio: str = Field(description="Nombre comercial exacto del negocio real encontrado")
    canton: str = Field(description="Cantón o provincia exacta")
    categoria: str = Field(description="Categoría o nicho comercial")
    problema_detectado: str = Field(description="Cuello de botella operativo o falla en atención al cliente")
    contacto: str = Field(description="Teléfono de WhatsApp o e-mail de contacto público encontrado")

class ListaLeads(BaseModel):
    leads: List[Lead] = Field(description="Lista de potenciales clientes reales detectados")

# ==========================================
# 2. LÓGICA DEL AGENTE INVESTIGADOR
# ==========================================

def ejecutar_agente_1(nicho: str, provincia_canton: str, limite: int = 2) -> ListaLeads:
    """
    Agente 1: Busca prospectos y los estructura a formato Pydantic usando identificadores de modelo v1beta válidos.
    """
    # Identificador estandarizado y compatible con v1beta
    MODELO_ACTIVO = "gemini-2.5-flash"

    try:
        prompt_busqueda = f"""
        Busca en internet negocios REALES y actualmente OPERATIVOS del nicho '{nicho}' en la zona de '{provincia_canton}', Ecuador.
        Extrae exactamente {limite} establecimientos.

        Para cada uno obtén:
        - Nombre comercial real.
        - Cantón/Ubicación.
        - Teléfono o WhatsApp real de contacto público / correo electrónico.
        - Oportunidad de mejora en su atención o ventas.
        """

        respuesta_raw = None

        # PASO 1: Generación con SDK Google GenAI
        keys_disponibles = config.api_keys
        api_key_actual = config.obtener_siguiente_key()

        for intento in range(len(keys_disponibles)):
            try:
                client = genai.Client(api_key=api_key_actual)
                response = client.models.generate_content(
                    model=MODELO_ACTIVO,
                    contents=prompt_busqueda,
                )
                respuesta_raw = response.text
                break  # Éxito: sale del bucle

            except (APIError, Exception) as e:
                error_str = str(e)
                if any(err in error_str for err in ["429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE"]):
                    api_key_actual = config.obtener_siguiente_key()
                    print(f"⚠️ Servidor ocupado o cuota agotada. Rotando a la siguiente API Key (Intento {intento + 1}/{len(keys_disponibles)})...")
                    time.sleep(2)
                else:
                    print(f"❌ Error inesperado en Agente 1 (Búsqueda): {e}")
                    break

        if not respuesta_raw or len(str(respuesta_raw).strip()) < 20:
            return ListaLeads(leads=[])

        time.sleep(1)

        # PASO 2: Estructuración Pydantic con LangChain
        prompt_formato = f"""
        Convierte la siguiente información sobre negocios reales en la estructura Pydantic requerida:

        DATOS ENCONTRADOS:
        {respuesta_raw}
        """

        for intento in range(len(keys_disponibles)):
            try:
                llm_estructurador = ChatGoogleGenerativeAI(
                    model=MODELO_ACTIVO,
                    google_api_key=config.obtener_siguiente_key()
                ).with_structured_output(ListaLeads, method="json_schema")

                return llm_estructurador.invoke(prompt_formato)
            except Exception as e:
                error_str = str(e)
                if any(err in error_str for err in ["429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE"]):
                    print(f"⚠️ Reintentando estructuración con nueva API Key...")
                    time.sleep(2)
                else:
                    print(f"❌ Error en estructuración Pydantic: {e}")
                    break

        return ListaLeads(leads=[])

    except Exception as e:
        print(f"❌ Error general en Agente 1: {e}")
        return ListaLeads(leads=[])