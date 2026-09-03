import csv
import asyncio
from agente_1_investigador import ejecutar_agente_1, Lead
from agente_2_estratega import agente_estratega_llm, PropuestaEstrategica
from database import guardar_prospectos
from config import config

async def procesar_lead_async(lead: Lead) -> dict:
    """Procesa un lead individual de manera asíncrona mediante el Agente 2."""
    prompt = f"""
    Actúa como un Consultor de Tecnología y Ventas B2B para negocios locales.
    Tu nombre es '{config.DESARROLLADOR_NOMBRE}' de '{config.AGENCIA_NOMBRE}'.
    
    Analiza el siguiente prospecto:
    - Negocio: {lead.nombre_negocio} ({lead.canton})
    - Categoría: {lead.categoria}
    - Problema Detectado: {lead.problema_detectado}
    
    Tu tarea:
    1. Elabora un diagnóstico breve del impacto negativo de su problema.
    2. Diseña una propuesta de solución de software/automatización.
    3. Escribe un mensaje corto para WhatsApp listo para enviar al dueño.
       REGLA OBLIGATORIA: Preséntate con el nombre '{config.DESARROLLADOR_NOMBRE}'. Sin corchetes ni textos vacíos.
    """
    
    try:
        estrategia: PropuestaEstrategica = await agente_estratega_llm.ainvoke(prompt)
        return {
            "negocio": estrategia.nombre_negocio,
            "contacto": lead.contacto,
            "diagnostico": estrategia.diagnostico_clave,
            "solucion": estrategia.solucion_propuesta,
            "pitch_whatsapp": estrategia.mensaje_pitch_whatsapp
        }
    except Exception as e:
        print(f"-> Error procesando lead {lead.nombre_negocio}: {e}")
        return None

async def ejecutar_pipeline_dinamico():
    print("==================================================")
    print("   PIPELINE MULTIAGENTE DE PROSPECCIÓN (PROD)    ")
    print("==================================================\n")
    
    # 1. Captura de parámetros dinámicos
    nicho = input("Ingresa el nicho a investigar (ej. Ferreterías, Hosterías, Resto-bars): ").strip()
    ubicacion = input("Ingresa la ciudad o provincia (ej. Tena, Macas, Puyo, Quito): ").strip()
    
    if not nicho or not ubicacion:
        print("Error: El nicho y la ubicación son obligatorios.")
        return

    # 2. Ejecución Agente 1 (Investigador)
    print(f"\n[Agente 1] Buscando oportunidades para '{nicho}' en '{ubicacion}'...")
    investigacion = ejecutar_agente_1(nicho=nicho, provincia_canton=ubicacion, limite=3)
    
    if not investigacion.leads:
        print("No se encontraron prospectos. Abortando.")
        return

    # 3. Ejecución Agente 2 en Paralelo (Estratega)
    print(f"\n[Agente 2] Procesando {len(investigacion.leads)} leads en paralelo...")
    tareas = [procesar_lead_async(lead) for lead in investigacion.leads]
    resultados_brutos = await asyncio.gather(*tareas)
    
    # Filtrar posibles ejecuciones con error
    resultados_finales = [r for r in resultados_brutos if r is not None]

    if not resultados_finales:
        print("No se generaron estrategias válidas.")
        return

    # 4. Persistencia en Base de Datos MySQL
    print("\n[Base de Datos] Guardando registros en MySQL Workbench...")
    guardar_prospectos(resultados_finales)

    # 5. Persistencia de Respaldo en CSV (utf-8-sig)
    nombre_archivo = f"prospectos_{nicho.lower().replace(' ', '_')}.csv"
    with open(nombre_archivo, mode="w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(
            file, 
            fieldnames=["negocio", "contacto", "diagnostico", "solucion", "pitch_whatsapp"]
        )
        writer.writeheader()
        writer.writerows(resultados_finales)
        
    print(f"-> Respaldo CSV generado: {nombre_archivo}")
    print("\n¡Pipeline completado exitosamente!")

if __name__ == "__main__":
    asyncio.run(ejecutar_pipeline_dinamico())