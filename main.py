import time
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Status, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Importación de los agentes existentes
from agente_1_investigador import ejecutar_agente_1
from agente_2_estratega import ejecutar_agente_2
from agente_3_validador import ejecutar_agente_3
from agente_4_despachador import ejecutar_agente_4

# ==========================================
# 1. CONFIGURACIÓN DE LA APLICACIÓN FASTAPI
# ==========================================

app = FastAPI(
    title="LabShop Lead Engine API",
    description="API REST Pro de prospección comercial B2B impulsada por arquitectura multiagente.",
    version="1.0.0"
)

# Configuración de CORS para permitir peticiones desde cualquier frontend (Next.js/React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 2. MODELOS DE DATOS (SCHEMAS HTTP)
# ==========================================

class SolicitudProspeccion(BaseModel):
    nicho: str = Field(..., example="Ferreterías", description="Nicho de mercado a investigar")
    ubicacion: str = Field(..., example="Tena", description="Ciudad o provincia objetivo")
    cantidad_leads: int = Field(default=3, ge=1, le=10, description="Número de prospectos a procesar (Máx 10)")

class ProspectoProcesado(BaseModel):
    nombre_empresa: str
    contacto_original: str
    contacto_limpio: str
    tipo_contacto: str
    prioridad: str
    es_valido: bool
    motivo_rechazo: Optional[str] = ""
    propuesta_comercial: str
    enlace_despacho: str

class RespuestaProspeccion(BaseModel):
    exito: bool
    total_procesados: int
    total_validos: int
    tiempo_ejecucion_segundos: float
    prospectos: List[ProspectoProcesado]

# ==========================================
# 3. ENDPOINTS DE LA API
# ==========================================

@app.get("/", tags=["Estado"])
def verificar_estado():
    """Endpoint básico de salud (Healthcheck) para verificar que el servidor esté activo."""
    return {"status": "online", "servicio": "LabShop Lead Engine API", "version": "1.0.0"}

@app.post("/api/v1/prospectar", response_model=RespuestaProspeccion, tags=["Prospección"])
async def ejecutar_pipeline_prospeccion(solicitud: SolicitudProspeccion):
    """
    Ejecuta el pipeline completo de los 4 agentes de forma secuencial:
    1. Agente 1: Busca e identifica empresas.
    2. Agente 2: Genera estrategia y pitch.
    3. Agente 3: Valida técnicamente (E.164 / DNS MX) y prioriza.
    4. Agente 4: Genera enlaces de despacho (wa.me / mailto:).
    """
    tiempo_inicio = time.time()
    prospectos_finales = []

    try:
        # Agente 1: Búsqueda de Leads
        leads_raw = ejecutar_agente_1(solicitud.nicho, solicitud.ubicacion, solicitud.cantidad_leads)
        
        if not leads_raw:
            raise HTTPException(
                status_code=Status.HTTP_444_NO_RESPONSE,
                detail="No se encontraron prospectos para los criterios especificados."
            )

        for lead in leads_raw:
            # Extraer campos base devueltos por Agente 1
            nombre = lead.get("nombre", "Empresa desconocida")
            contacto_raw = lead.get("contacto", "")
            problema = lead.get("problema_detectado", "Atención al cliente deficiente.")

            # Agente 2: Estrategia y Redacción del Pitch
            propuesta_texto = ejecutar_agente_2(nombre, problema)

            # Agente 3: Validación Técnica (Python + MX + E.164) y Priorización
            val_res = ejecutar_agente_3(contacto_raw, problema)

            # Agente 4: Enrutamiento y Enlace
            enlace = ""
            if val_res.es_contacto_valido:
                enlace = ejecutar_agente_4(val_res.contacto_limpio, val_res.tipo_contacto, propuesta_texto)

            prospectos_finales.append(ProspectoProcesado(
                nombre_empresa=nombre,
                contacto_original=contacto_raw,
                contacto_limpio=val_res.contacto_limpio,
                tipo_contacto=val_res.tipo_contacto,
                prioridad=val_res.prioridad,
                es_valido=val_res.es_contacto_valido,
                motivo_rechazo=val_res.motivo_rechazo,
                propuesta_comercial=propuesta_texto,
                enlace_despacho=enlace
            ))

        tiempo_total = round(time.time() - tiempo_inicio, 2)
        validos_count = sum(1 for p in prospectos_finales if p.es_valido)

        return RespuestaProspeccion(
            exito=True,
            total_procesados=len(prospectos_finales),
            total_validos=validos_count,
            tiempo_ejecucion_segundos=tiempo_total,
            prospectos=prospectos_finales
        )

    except Exception as e:
        raise HTTPException(
            status_code=Status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno durante la prospección: {str(e)}"
        )