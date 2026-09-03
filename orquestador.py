import csv
from agente_1_investigador import ejecutar_agente_1
from agente_2_estratega import ejecutar_agente_2

def ejecutar_pipeline():
    print("--- INICIANDO PIPELINE DE AGENTES ---")
    
    # 1. Extracción de prospectos (Agente 1)
    investigacion = ejecutar_agente_1("Hosterías y Turismo Ecológico", "Tena, Napo")
    
    if not investigacion.leads:
        print("No se encontraron leads. Abortando.")
        return
        
    resultados_finales = []
    
    # 2. Procesamiento estratégico por cada prospecto (Agente 2)
    for lead in investigacion.leads:
        print(f"Generando estrategia para: {lead.nombre_negocio}...")
        estrategia = ejecutar_agente_2(lead, nombre_desarrollador="Favian C.")
        
        resultados_finales.append({
            "negocio": estrategia.nombre_negocio,
            "contacto": lead.contacto_simulado,
            "diagnostico": estrategia.diagnostico_clave,
            "solucion": estrategia.solucion_propuesta,
            "pitch_whatsapp": estrategia.mensaje_pitch_whatsapp
        })
        
    # 3. Persistencia de datos en CSV (utf-8-sig para evitar tildes corruptas en Windows/Excel)
    archivo_csv = "estrategias_comerciales.csv"
    with open(archivo_csv, mode="w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(
            file, 
            fieldnames=["negocio", "contacto", "diagnostico", "solucion", "pitch_whatsapp"]
        )
        writer.writeheader()
        writer.writerows(resultados_finales)
        
    print(f"\nEjecución finalizada. Los datos listos para consumo se guardaron en: {archivo_csv}")

if __name__ == "__main__":
    ejecutar_pipeline()