import cloudscraper
from bs4 import BeautifulSoup
import time
import random
import re

# --- FUNCIÓN DE GÉNERO SIMPLIFICADA ---
def normalizar_genero(lista_generos_crudos):
    """
    Ya no agrupa. Simplemente toma el género más específico.
    Si AOTY da ['Black Metal', 'Death Metal'], devuelve 'Black Metal'.
    """
    if not lista_generos_crudos:
        return "N/A"
    
    # Devolvemos el primer género de la lista (suele ser el principal)
    # También capitalizamos bien el texto (ej: "black metal" -> "Black Metal")
    genero_limpio = lista_generos_crudos[0].strip().title()
    return genero_limpio

def formatear_fecha(fecha_sucia):
    try:
        partes = fecha_sucia.replace(",", "").split()
        meses = {"January": "01", "February": "02", "March": "03", "April": "04", "May": "05", "June": "06", "July": "07", "August": "08", "September": "09", "October": "10", "November": "11", "December": "12"}
        if len(partes) >= 3:
            mes = meses.get(partes[0], "00")
            dia = partes[1].zfill(2)
            anio = partes[2]
            return f"{dia}/{mes}/{anio}"
        return fecha_sucia
    except: return fecha_sucia

def obtener_origen_artista(scraper, artist_url):
    if not artist_url: return "N/A"
    try:
        resp = scraper.get(artist_url, timeout=5)
        if resp.status_code != 200: return "N/A"
        soup = BeautifulSoup(resp.text, 'html.parser')
        rows = soup.find_all('div', class_='artistDetailRow')
        for row in rows:
            txt = row.text.lower()
            if "formed" in txt or "born" in txt or "origin" in txt:
                clean_text = row.text.strip()
                if " in " in clean_text.lower():
                    return clean_text.lower().split(" in ")[-1].strip().title()
                return clean_text
        return "N/A"
    except: return "N/A"

def obtener_datos_album(scraper, url):
    try:
        resp = scraper.get(url, timeout=10)
        if resp.status_code != 200: return None
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        headline = soup.find('div', class_='albumHeadline')
        if not headline: return None
        
        artist_tag = headline.find('div', class_='artist')
        artista = artist_tag.text.strip() if artist_tag else "N/A"
        
        artist_url = None
        if artist_tag and artist_tag.find('a'):
            href = artist_tag.find('a')['href']
            artist_url = "https://www.albumoftheyear.org" + href

        album_tag = headline.find(['h1', 'div'], class_='albumTitle')
        album = album_tag.text.strip() if album_tag else "N/A"

        fecha, genero = "N/A", "N/A"
        for row in soup.find_all('div', class_='detailRow'):
            txt = row.text
            if "Release Date" in txt:
                fecha_cruda = txt.replace("Release Date", "").strip()
                fecha = formatear_fecha(fecha_cruda)
            elif "Genre" in txt:
                tags = [a.text.strip() for a in row.find_all('a')]
                genero = normalizar_genero(tags)

        link_streaming = "No disponible"
        
        btn_spotify = soup.find('div', class_='albumButton spotify')
        if btn_spotify:
            link = btn_spotify.find_parent('a')
            if link and link.has_attr('href'):
                link_streaming = link['href']
                if not link_streaming.startswith("http"): link_streaming = "https://www.albumoftheyear.org" + link_streaming

        if link_streaming == "No disponible":
            btn_bandcamp = soup.find('div', class_='albumButton bandcamp')
            if btn_bandcamp:
                link = btn_bandcamp.find_parent('a')
                if link and link.has_attr('href'):
                    link_streaming = link['href']
                    if not link_streaming.startswith("http"): link_streaming = "https://www.albumoftheyear.org" + link_streaming

        if link_streaming == "No disponible": return None

        origen = obtener_origen_artista(scraper, artist_url)

        return {
            'Artista': artista, 'Álbum': album, 'Género': genero, 
            'Fecha': fecha, 'Spotify URL': link_streaming, 'Origen': origen
        }
    except Exception: return None

def ejecutar_scraper(url_inicial, callback_progress=None):
    scraper = cloudscraper.create_scraper()
    todos_los_discos = []
    pagina = 1
    url_actual = url_inicial
    
    while True:
        if callback_progress: callback_progress(f"Procesando página {pagina}...")
        try: r = scraper.get(url_actual, timeout=15)
        except Exception: break
        if r.status_code != 200: break
        
        soup = BeautifulSoup(r.text, 'html.parser')
        blocks = soup.find_all('div', class_='albumBlock')
        if not blocks: blocks = soup.find_all('div', class_='albumListRow')
        if not blocks: break
        
        links = ["https://www.albumoftheyear.org" + b.find('a')['href'] for b in blocks if b.find('a') and b.find('a').has_attr('href')]
        
        for link in links:
            time.sleep(random.uniform(0.3, 0.6))
            datos = obtener_datos_album(scraper, link)
            if datos: todos_los_discos.append(datos)
        
        if len(links) < 60: break
        pagina += 1
        if pagina == 2: url_actual = url_inicial.rstrip('/') + f"/{pagina}/"
        else: url_actual = re.sub(r'(/\d+/?)$', f'/{pagina}/', url_actual.rstrip("/"))

    return todos_los_discos

def obtener_generos_mes(year, month_val, month_name):
    """
    Intenta cargar géneros de la URL específica del mes.
    Si falla (404/Futura), hace fallback a la página general.
    """
    cache_key = f"{year}_{month_val}"
    if hasattr(obtener_generos_mes, "cache") and cache_key in obtener_generos_mes.cache:
        return obtener_generos_mes.cache[cache_key]

    scraper = cloudscraper.create_scraper()
    
    # 1. Intentar URL específica del mes
    target_url = f"https://www.albumoftheyear.org/{year}/releases/"
    if month_val:
        target_url += f"{month_name.lower()}-{month_val}/"

    r = None
    try:
        r = scraper.get(target_url, timeout=10)
    except:
        pass

    # 2. Si la URL del mes falla (ej: mes futuro no creado aún), usar fallback a portada
    if not r or r.status_code != 200:
        print(f"⚠️ No hay datos para {month_name} {year}. Cargando lista general...")
        try:
            r = scraper.get("https://www.albumoftheyear.org/releases/", timeout=10)
        except:
            return []

    if r.status_code != 200:
        return []

    soup = BeautifulSoup(r.text, 'html.parser')
    generos = []
    found_ids = set()
    links = soup.find_all('a', href=True)
    
    for link in links:
        href = link['href']
        # Buscamos ambos formatos: ?genre=14 o /genre/14-
        match = re.search(r'genre=(\d+)', href)
        if not match:
            match = re.search(r'/genre/(\d+)', href)
            
        if match:
            gid = match.group(1)
            if gid not in found_ids:
                nombre = link.text.strip()
                if nombre:
                    generos.append({'nombre': nombre, 'id': gid})
                    found_ids.add(gid)
    
    generos = sorted(generos, key=lambda x: x['nombre'])
    
    if not hasattr(obtener_generos_mes, "cache"): obtener_generos_mes.cache = {}
    obtener_generos_mes.cache[cache_key] = generos
    return generos
