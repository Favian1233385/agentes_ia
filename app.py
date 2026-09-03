import streamlit as st
import pandas as pd
import time
from agente_1_investigador import ejecutar_agente_1
from agente_2_estratega import ejecutar_agente_2
from agente_3_validador import ejecutar_agente_3
from agente_4_despachador import ejecutar_agente_4
from database import guardar_prospectos, SessionLocal, ProspectoModel
from config import config

# Configuración del panel web
st.set_page_config(
    page_title="Panel de Prospección IA",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Sistema Multiagente de Prospección Comercial")
st.caption(f"Desarrollado por {config.DESARROLLADOR_NOMBRE} | {config.AGENCIA_NOMBRE}")

# Pestañas de navegación
tab_busqueda, tab_historial = st.tabs(["🔎 Nueva Investigación", "📊 Historial en Base de Datos"])

def ejecutar_con_reintento(funcion_agente, *args, retrazos=4, espera_base=30, **kwargs):
    """
    Ejecuta la función del agente y maneja el límite de cuota (429) 
    reintentando con un tiempo de espera progresivo (retroceso exponencial).
    """
    for intento in range(retrazos):
        try:
            return funcion_agente(*args, **kwargs)
        except Exception as e:
            codigo = getattr(e, "code", None)
            if callable(codigo):
                codigo = codigo()
            
            # Verificación de límite de API por código de estado o texto
            es_limite_api = (
                codigo == 429 
                or getattr(e, "status_code", None) == 429 
                or "429" in str(e) 
                or "ResourceExhausted" in type(e).__name__
            )
            
            if es_limite_api and intento < retrazos - 1:
                # Incrementa el tiempo de espera en cada intento (30s, 60s, 90s...)
                tiempo_espera = espera_base * (intento + 1)
                st.warning(f"⚠️ Cuota de API alcanzada (429). Esperando {tiempo_espera}s para reiniciar canal (Intento {intento + 1}/{retrazos})...")
                time.sleep(tiempo_espera)
            else:
                raise

# ==========================================
# PESTAÑA 1: NUEVA INVESTIGACIÓN
# ==========================================
with tab_busqueda:
    st.subheader("Configuración de Prospección")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        nicho = st.text_input("Nicho Comercial", placeholder="Ej. Ferreterías, Resto-bars, Hosterías")
    with col2:
        ubicacion = st.text_input("Ciudad / Provincia", placeholder="Ej. Tena, Macas, Puyo, Quito")
    with col3:
        limite = st.number_input("Cantidad de Leads", min_value=1, max_value=5, value=2)

    if st.button("🚀 Iniciar Prospección", type="primary"):
        if not nicho or not ubicacion:
            st.warning("Por favor completa el nicho y la ubicación.")
        else:
            try:
                # --------------------------------------------------
                # PASO 1: AGENTE 1 - INVESTIGADOR
                # --------------------------------------------------
                with st.spinner(f"🕵️‍♂️ Agente 1: Investigando '{nicho}' en '{ubicacion}'..."):
                    investigacion = ejecutar_con_reintento(
                        ejecutar_agente_1, 
                        nicho=nicho, 
                        provincia_canton=ubicacion, 
                        limite=limite
                    )
                
                if not investigacion or not getattr(investigacion, 'leads', None):
                    st.error("No se encontraron leads para esa búsqueda.")
                else:
                    st.success(f"✅ Agente 1 identificó {len(investigacion.leads)} leads!")
                    time.sleep(5)  # Pausa de enfriamiento tras consumo intensivo de búsqueda

                    # --------------------------------------------------
                    # PASO 2: AGENTE 2 - ESTRATEGA
                    # --------------------------------------------------
                    estrategias = []
                    with st.spinner("🎯 Agente 2: Diseñando propuestas comerciales..."):
                        for lead in investigacion.leads:
                            est = ejecutar_con_reintento(ejecutar_agente_2, lead)
                            estrategias.append(est)
                            time.sleep(4)  # Pausa entre cada lead para regular RPM
                    st.success("✅ Agente 2 completó el análisis.")
                    time.sleep(3)

                    # --------------------------------------------------
                    # PASO 3: AGENTE 3 - VALIDADOR
                    # --------------------------------------------------
                    validaciones = []
                    with st.spinner("🛡️ Agente 3: Validando números y contactos..."):
                        for lead in investigacion.leads:
                            valida = ejecutar_con_reintento(
                                ejecutar_agente_3, 
                                lead.contacto, 
                                lead.problema_detectado
                            )
                            validaciones.append(valida)
                            time.sleep(3)
                    st.success("✅ Agente 3 validó la información.")
                    time.sleep(2)

                    # --------------------------------------------------
                    # PASO 4: AGENTE 4 - DESPACHADOR
                    # --------------------------------------------------
                    despachos = []
                    with st.spinner("📲 Agente 4: Generando enlaces de despachos multicanal..."):
                        for val, est in zip(validaciones, estrategias):
                            despacho = ejecutar_con_reintento(
                                ejecutar_agente_4, 
                                val.contacto_limpio, 
                                est.mensaje_pitch_whatsapp,
                                tipo_contacto=val.tipo_contacto,
                                negocio=est.nombre_negocio
                            )
                            despachos.append(despacho)
                            time.sleep(2)
                    st.success("✅ Agente 4 generó los enlaces.")

                    # CONSOLIDACIÓN Y PERSISTENCIA
                    resultados_completos = []
                    for est, val, desp in zip(estrategias, validaciones, despachos):
                        resultados_completos.append({
                            "negocio": est.nombre_negocio,
                            "contacto": val.contacto_limpio,
                            "tipo_contacto": val.tipo_contacto,
                            "prioridad": val.prioridad,
                            "diagnostico": est.diagnostico_clave,
                            "solucion": est.solucion_propuesta,
                            "pitch_whatsapp": est.mensaje_pitch_whatsapp,
                            "url_wa": getattr(desp, 'url_despacho', getattr(desp, 'url_directa_wa', ''))
                        })

                    try:
                        guardar_prospectos(resultados_completos)
                        st.toast("Resultados almacenados en MySQL", icon="💾")
                    except Exception as e:
                        st.error(f"Error al guardar en BD: {e}")

                    # INTERFAZ DE RESULTADOS
                    st.subheader("Resultados Finales de Prospección")
                    for item in resultados_completos:
                        color_prio = "🔴" if item['prioridad'] == "Alta" else ("🟡" if item['prioridad'] == "Media" else "🟢")
                        
                        with st.expander(f"📍 {item['negocio']} | Contacto: {item['contacto']} ({item['tipo_contacto']}) | Prioridad: {color_prio} {item['prioridad']}"):
                            st.markdown(f"**Diagnóstico:** {item['diagnostico']}")
                            st.markdown(f"**Solución:** {item['solucion']}")
                            
                            # ETIQUETA DINÁMICA SEGÚN CANAL
                            etiqueta_canal = "Mensaje para Correo Electrónico:" if item['tipo_contacto'] == "Email" else "Mensaje de WhatsApp:"
                            st.text_area(etiqueta_canal, value=item['pitch_whatsapp'], height=120)

                            # BOTONES DE ACCIÓN DINÁMICOS
                            if item.get('url_wa'):
                                if item['tipo_contacto'] == "Email":
                                    st.link_button("✉️ Enviar Correo Electrónico", item['url_wa'], type="primary")
                                else:
                                    st.link_button("📲 Contactar por WhatsApp", item['url_wa'], type="primary")
                            else:
                                st.warning(f"⚠️ No se pudo generar el enlace de despacho para el canal {item['tipo_contacto']}.")

            except Exception as e:
                st.error(f"Ocurrió un error en la ejecución: {e}")

# ==========================================
# PESTAÑA 2: HISTORIAL BD (MYSQL)
# ==========================================
with tab_historial:
    st.subheader("Registros Almacenados en MySQL Workbench")
    if st.button("🔄 Actualizar Tabla"):
        st.rerun()

    db = SessionLocal()
    try:
        query = db.query(ProspectoModel).order_by(ProspectoModel.id.desc()).all()
        if query:
            data = [{
                "ID": p.id,
                "Negocio": p.negocio,
                "Contacto": p.contacto,
                "Canal": getattr(p, 'tipo_contacto', 'WhatsApp'),
                "Prioridad": getattr(p, 'prioridad', 'Media'),
                "Diagnóstico": p.diagnostico,
                "Solución": p.solucion,
                "Pitch WhatsApp": p.pitch_whatsapp,
                "Fecha": p.fecha_creacion
            } for p in query]
            
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hay registros almacenados en la base de datos.")
    except Exception as e:
        st.error(f"Error al leer la base de datos: {e}")
    finally:
        db.close()