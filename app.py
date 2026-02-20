import streamlit as st
import pandas as pd
import os
import time
import requests
from dotenv import load_dotenv
import datetime
import aoty_screaper
import checker_discos

# --- CONFIGURACIÓN ---
load_dotenv()
SPAM_USER = os.getenv("SPAM_USER")
SPAM_PASS = os.getenv("SPAM_PASS")

st.set_page_config(page_title="Music Manager Suite", layout="wide")

# --- SESIÓN ---
# Inicializamos 'missing_results' como None para evitar el bug de los globos al inicio
if 'scrape_results' not in st.session_state:
    st.session_state['scrape_results'] = []
if 'missing_results' not in st.session_state:
    st.session_state['missing_results'] = None

# --- BARRA LATERAL ---
st.sidebar.title("🎛️ Panel de Control")
modulo = st.sidebar.radio("Herramienta:", ["📥 Scraper AOTY", "🔍 Checker Discos", "⚙️ Config"])

st.sidebar.markdown("---")
if st.session_state['scrape_results']:
    st.sidebar.success(f"{len(st.session_state['scrape_results'])} discos en memoria.")
else:
    st.sidebar.info("Memoria vacía.")

# --- MÓDULO 1: SCRAPER AOTY ---
if modulo == "📥 Scraper AOTY":
    st.title("📥 Scraper AOTY (Multigénero)")
    st.markdown("Extrae discos manteniendo el género específico (ej: 'Black Metal').")

    meses = {
        "Todos": "", "January": "01", "February": "02", "March": "03", 
        "April": "04", "May": "05", "June": "06", "July": "07", 
        "August": "08", "September": "09", "October": "10", 
        "November": "11", "December": "12"
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        current_year = datetime.date.today().year
        year = st.selectbox("Año", list(range(current_year + 1, 1999, -1)), index=1)
        month_sel = st.selectbox("Mes", options=list(meses.keys()))
        month_val = meses[month_sel]

    # --- CARGA DINÁMICA DE GÉNEROS ---
    with st.spinner(f"Cargando géneros para {month_sel} {year}..."):
        lista_generos = aoty_screaper.obtener_generos_mes(year, month_val, month_sel)
    
    if not lista_generos:
        lista_nombres = ["Todos"]
        mapa_ids = {"Todos": ""}
    else:
        lista_nombres = ["Todos"] + [g['nombre'] for g in lista_generos]
        mapa_ids = {g['nombre']: g['id'] for g in lista_generos}
        mapa_ids["Todos"] = ""

    with col2:
        selected_genres = st.multiselect(
            "Géneros (Múltiple)", 
            options=lista_nombres, 
            default=["Todos"],
            help="Si seleccionas 'Todos', se ignoran otros géneros."
        )

        release_types = {"Todos": "", "LP": "lp", "EP": "ep", "Single": "single", "Mixtape": "mixtape", "Demo": "demo", "Video": "video"}
        type_options = list(release_types.keys())
        selected_types = st.multiselect("Tipo de Release (Múltiple)", options=type_options, default=["Todos"])

    # --- EJECUCIÓN SCRAPER ---
    if st.button("🚀 Ejecutar Búsqueda Combinada", type="primary"):
        if not selected_genres: st.error("Selecciona al menos un género."); st.stop()
        if not selected_types: st.error("Selecciona al menos un tipo."); st.stop()

        genres_to_scan = []
        if "Todos" in selected_genres:
            genres_to_scan = [("", "Todos")]
        else:
            for g_name in selected_genres:
                if g_name in mapa_ids:
                    genres_to_scan.append((mapa_ids[g_name], g_name))

        types_to_scan = []
        if "Todos" in selected_types:
            types_to_scan = [("", "Todos")]
        else:
            for t_name in selected_types:
                types_to_scan.append((release_types[t_name], t_name))

        total_combinaciones = len(genres_to_scan) * len(types_to_scan)
        st.info(f"Se procesarán {total_combinaciones} combinaciones de filtros.")
        
        resultados_totales = []
        bar = st.progress(0, text="Iniciando escaneo masivo...")
        counter = 0
        
        for g_id, g_name in genres_to_scan:
            for t_id, t_name in types_to_scan:
                counter += 1
                status_text = f"Escaneando: {g_name} / {t_name} ({counter}/{total_combinaciones})"
                bar.progress(counter / total_combinaciones, text=status_text)
                
                base_url = f"https://www.albumoftheyear.org/{year}/releases/"
                if month_val: base_url += f"{month_sel.lower()}-{month_val}/"
                
                params = []
                if g_id: params.append(f"genre={g_id}")
                if t_id: params.append(f"type={t_id}")
                
                final_url = base_url
                if params: final_url += "?" + "&".join(params)
                
                res_parcial = aoty_screaper.ejecutar_scraper(final_url)
                if res_parcial:
                    resultados_totales.extend(res_parcial)

        bar.progress(1.0, text="Limpiando duplicados...")
        
        if resultados_totales:
            df_final = pd.DataFrame(resultados_totales)
            df_final = df_final.drop_duplicates(subset=['Spotify URL'], keep='first')
            st.session_state['scrape_results'] = df_final.to_dict('records')
            bar.empty()
            st.success(f"✅ ¡Scrapeo completado! {len(df_final)} álbumes únicos encontrados.")
        else:
            bar.empty()
            st.warning("No se encontraron resultados.")

    # --- VISUALIZACIÓN SCRAPER ---
    if st.session_state['scrape_results']:
        st.markdown("### 📊 Resultados Actuales")
        df = pd.DataFrame(st.session_state['scrape_results'])
        cols_order = ['Artista', 'Álbum', 'Género', 'Origen', 'Fecha', 'Spotify URL']
        cols_exist = [c for c in cols_order if c in df.columns]
        df = df[cols_exist]
        st.dataframe(df, width='stretch')
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Descargar CSV", data=csv, file_name='aoty_scrape.csv', mime='text/csv')

# --- MÓDULO 2: CHECKER DISCOS (CORREGIDO) ---
elif modulo == "🔍 Checker Discos":
    st.title("🔍 Verificar y Corregir Metadatos")
    
    if not SPAM_USER or not SPAM_PASS:
        st.error("❌ Credenciales no encontradas. Configura el archivo `.env`.")
        st.stop()

    st.markdown("### 1. Origen de los datos")
    fuente = st.radio("¿De dónde vienen los datos?", ["Desde Memoria (Scraper)", "Subir CSV manualmente"], horizontal=True)
    
    datos_input = []
    
    if fuente == "Subir CSV manualmente":
        uploaded_file = st.file_uploader("Sube tu archivo CSV", type=['csv'])
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                if 'Artista' in df.columns and 'Álbum' in df.columns:
                    datos_input = df.to_dict('records')
                    st.info(f"📂 Archivo cargado: {len(datos_input)} registros.")
            except Exception as e:
                st.error(f"Error leyendo CSV: {e}")
    
    elif fuente == "Desde Memoria (Scraper)":
        if st.session_state['scrape_results']:
            datos_input = st.session_state['scrape_results']
            st.info(f"🧠 Usando {len(datos_input)} discos de la sesión actual.")
        else:
            st.warning("⚠️ Memoria vacía. Ejecuta el Scraper primero.")

    if datos_input:
        genero_default = st.text_input("Género por defecto", value="")
        
        # PASO 1: VERIFICAR
        if st.button("▶️ Verificar Faltantes en SpamMusic", type="primary"):
            with st.spinner("⏳ Ejecutando Selenium..."):
                progress_bar = st.progress(0, text="Preparando...")
                status_text = st.empty()
                
                def update_checker_progress(current, total, album):
                    pct = int((current / total) * 100)
                    progress_bar.progress(pct, text="Progreso global")
                    status_text.text(f"Analizando: {album} ({current}/{total})")

                lista_faltantes = checker_discos.ejecutar_checker(
                    lista_discos=datos_input,
                    user=SPAM_USER,
                    password=SPAM_PASS,
                    genero_default=genero_default,
                    callback_progress=update_checker_progress
                )
                
                # Guardamos resultado (aunque sea vacío) para indicar que el proceso terminó
                st.session_state['missing_results'] = lista_faltantes
        
        # PASO 2: ENRIQUECER Y EDITAR
        # Solo entramos si missing_results NO es None (es decir, si el checkeo se ha ejecutado)
        if st.session_state['missing_results'] is not None:
            
            # Si la lista tiene datos, mostramos la tabla y el enriquecimiento
            if len(st.session_state['missing_results']) > 0:
                df_missing = pd.DataFrame(st.session_state['missing_results'])
                
                st.markdown("### 🧹 Paso 2: Completar Origen (MusicBrainz)")
                st.info("Prioridad: Mantener Género de AOTY. Buscar País en MusicBrainz.")
                
                mb_email = st.text_input("Email para User-Agent", value="test@example.com")
                
                if st.button("🚀 Buscar Origen (Con reintentos)"):
                    headers = {'User-Agent': f'MusicManagerApp/1.0 ( {mb_email} )'}
                    total = len(df_missing)
                    
                    debug_expander = st.expander("🖥️ Consola de Depuración", expanded=True)
                    with debug_expander:
                        log_area = st.empty()
                        progress_bar_mb = st.progress(0)
                    
                    logs = []
                    
                    for i, row in df_missing.iterrows():
                        artista = row['Artista']
                        album = row['Álbum']
                        current_genre = row.get('Género', 'N/A')
                        
                        logs.append(f"🔍 [{i+1}/{total}] **{artista}** - *{album}*")
                        
                        # Lógica de Género: Si AOTY ya tiene género, NO lo tocamos.
                        # (El género ya viene del scraper con su nombre real)
                        
                        # --- LÓGICA DE PAÍS CON REINTENTOS ---
                        pais_encontrado = False
                        intentos = 0
                        max_intentos = 3
                        
                        while not pais_encontrado and intentos < max_intentos:
                            intentos += 1
                            try:
                                url_artist = f"https://musicbrainz.org/ws/2/artist/?query=artist:{artista}&fmt=json&limit=1"
                                r_art = requests.get(url_artist, headers=headers, timeout=15)
                                
                                if r_art.status_code == 200:
                                    data = r_art.json()
                                    if 'artists' in data and len(data['artists']) > 0:
                                        best_match = data['artists'][0]
                                        score = best_match.get('score', 0)
                                        country = best_match.get('country', None)
                                        
                                        if score > 80 and country:
                                            df_missing.at[i, 'Origen'] = country
                                            logs.append(f"   🌍 País: {country} (Score: {score}%)")
                                            pais_encontrado = True
                                        elif score > 80 and not country:
                                            logs.append(f"   ⚠️ Artista encontrado pero sin país.")
                                            pais_encontrado = True
                                        else:
                                            logs.append(f"   ⚠️ Baja coincidencia (Score: {score}%).")
                                            pais_encontrado = True
                                    else:
                                        logs.append(f"   ❌ Artista no encontrado.")
                                        pais_encontrado = True
                                else:
                                    logs.append(f"   ⚠️ Error Server: {r_art.status_code}. Reintentando...")
                            
                            except Exception as e:
                                error_msg = str(e)
                                if "ConnectionAbortedError" in error_msg or "RemoteDisconnected" in error_msg or "ConnectionError" in error_msg:
                                    logs.append(f"   💥 Conexión abortada. Reintentando ({intentos}/{max_intentos})...")
                                    time.sleep(2)
                                else:
                                    logs.append(f"   💥 Error: {e}")
                                    pais_encontrado = True
                        
                        log_area.markdown("\n".join(logs))
                        progress_bar_mb.progress((i+1)/total)
                        time.sleep(1.1)

                    logs.append("\n✅ **PROCESO FINALIZADO**")
                    log_area.markdown("\n".join(logs))
                    st.session_state['missing_results'] = df_missing.to_dict('records')

                # EDICIÓN MANUAL
                st.markdown("#### 📝 Tabla Final (Editable)")
                st.warning("👀 Revisa los datos. Puedes editar cualquier celda haciendo doble click.")
                
                edited_df = st.data_editor(
                    df_missing, 
                    num_rows="dynamic", 
                    width='stretch',
                    column_config={
                        "Spotify URL": st.column_config.LinkColumn("Link"),
                        "Origen": st.column_config.TextColumn("País 🌍")
                    }
                )

                csv_final = edited_df.to_csv(index=False).encode('utf-8')
                st.download_button("⬇️ Descargar CSV Limpio", csv_final, "discos_faltantes_final.csv")
            
            # Si la lista está vacía (pero no None), significa que el checkeo terminó y todo OK
            else:
                st.balloons()
                st.success("🎉 ¡Todo al día! No faltan discos.")

# --- MÓDULO 3: CONFIGURACIÓN ---
elif modulo == "⚙️ Config":
    st.title("⚙️ Ajustes y Ayuda")
    st.markdown("#### Credenciales actuales")
    st.write(f"Usuario: `{SPAM_USER if SPAM_USER else 'NO CONFIGURADO'}`")
    
    st.markdown("#### Requisitos")
    st.code("pip install streamlit pandas python-dotenv selenium cloudscraper beautifulsoup4 requests", language='bash')
    
    st.markdown("#### Nota sobre Géneros")
    st.info("El scraper ahora guarda el género específico (ej: 'Black Metal') en lugar de agrupar. "
            "MusicBrainz solo se usará para buscar el País de origen.")
