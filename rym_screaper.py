import cloudscraper
from bs4 import BeautifulSoup
import csv
import time
import random

# --- DICCIONARIO FECHAS ---
meses_en_a_es = {
    "January": "01", "February": "02", "March": "03", "April": "04",
    "May": "05", "June": "06", "July": "07", "August": "08",
    "September": "09", "October": "10", "November": "11", "December": "12"
}

def formatear_fecha(fecha_sucia):
    try:
        limpia = fecha_sucia.replace("/", "").strip().replace(",", "")
        partes = limpia.split()
        if len(partes) >= 3:
            mes_num = meses_en_a_es.get(partes[0], "00")
            dia_num = partes[1].zfill(2)
            anio = partes[2]
            return f"{dia_num}/{mes_num}/{anio}"
        return fecha_sucia
    except:
        return fecha_sucia

# --- INICIO DEL PROGRAMA ---
print("--- SCRAPER AOTY: SOLO DATOS PEDIDOS ---")

url_inicial = input("1. Pega la URL de la página 1: ")
nombre_csv = input("2. Nombre para el archivo (ej: mis_discos): ")

if not nombre_csv.endswith('.csv'):
    nombre_csv += '.csv'

scraper = cloudscraper.create_scraper()

try:
    with open(nombre_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # --- CABECERA EXACTA ---
        writer.writerow(['Artista', 'Álbum', 'Género', 'Fecha', 'Spotify URL'])
        
        pagina_actual = 1
        url_actual = url_inicial

        while True:
            print(f"\n🚀 --- PROCESANDO PÁGINA {pagina_actual} ---")
            print(f"URL: {url_actual}")

            response = scraper.get(url_actual)
            
            if response.status_code != 200:
                print(f"❌ Error {response.status_code}. No se pudo acceder.")
                break

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscamos los bloques de discos
            album_blocks = soup.find_all('div', class_='albumBlock')
            if not album_blocks:
                album_blocks = soup.find_all('div', class_='albumListRow')

            if not album_blocks:
                print("⚠️ No se encontraron discos. Fin.")
                break

            links_para_visitar = []
            for block in album_blocks:
                link_tag = block.find('a')
                if link_tag and 'href' in link_tag.attrs:
                    full_link = "https://www.albumoftheyear.org" + link_tag['href']
                    links_para_visitar.append(full_link)

            total_discos = len(links_para_visitar)
            print(f"✅ Detectados {total_discos} discos.")
            
            contador = 0
            
            for album_url in links_para_visitar:
                contador += 1
                
                # Pausa breve
                time.sleep(random.uniform(0.5, 1.2))
                
                try:
                    resp_album = scraper.get(album_url)
                    if resp_album.status_code == 200:
                        page = BeautifulSoup(resp_album.text, 'html.parser')

                        # --- 1. DATOS BÁSICOS ---
                        headline = page.find('div', class_='albumHeadline')
                        artista = "ERROR"
                        album_nombre = "ERROR"

                        if headline:
                            artist_div = headline.find('div', class_='artist')
                            if artist_div: artista = artist_div.text.strip()
                            
                            title_tag = headline.find('h1', class_='albumTitle')
                            if not title_tag: title_tag = headline.find('div', class_='albumTitle')
                            if title_tag: album_nombre = title_tag.text.strip()

                        # --- 2. DETALLES (Fecha y Género) ---
                        fecha_final = "N/A"
                        generos = "N/A"
                        rows = page.find_all('div', class_='detailRow')
                        for row in rows:
                            txt = row.text.strip()
                            if "Release Date" in txt:
                                fecha_cruda = txt.replace("Release Date", "").strip()
                                fecha_final = formatear_fecha(fecha_cruda)
                            
                            if "Genre" in txt:
                                tags = row.find_all('a')
                                lista_gen = [t.text.strip() for t in tags]
                                generos = ", ".join(lista_gen)

                        # --- 3. SPOTIFY ---
                        spotify_link = "No disponible"
                        div_boton = page.find('div', class_='albumButton spotify')
                        if div_boton:
                            link_padre = div_boton.find_parent('a')
                            if link_padre and 'href' in link_padre.attrs:
                                href = link_padre['href']
                                spotify_link = "https://www.albumoftheyear.org" + href if href.startswith("/") else href

                        print(f"[{contador}/{total_discos}] 🎵 {artista} - {album_nombre}")
                        
                        # --- GUARDAR EN CSV ---
                        writer.writerow([artista, album_nombre, generos, fecha_final, spotify_link])

                    else:
                        print(f"❌ Error disco {resp_album.status_code}")

                except Exception as e:
                    print(f"⚠️ Error procesando: {e}")

            # --- PAGINACIÓN ---
            continuar = input(f"\n¿Procesar página {pagina_actual + 1}? (s/n): ").lower()
            if continuar in ['s', 'si', 'y']:
                if pagina_actual == 1:
                    url_actual = url_inicial.replace("/releases/", f"/releases/{pagina_actual + 1}/")
                else:
                    url_actual = url_actual.replace(f"/releases/{pagina_actual}/", f"/releases/{pagina_actual + 1}/")
                pagina_actual += 1
            else:
                break

    print(f"\n🎉 ¡LISTO! Datos en: {nombre_csv}")

except Exception as e:
    print(f"\n❌ Error General: {e}")

input("Enter para salir.")