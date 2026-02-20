import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

VARIACIONES_SELF_TITLED = [
    "self titled", "self-titled", "selftitled", "self_titled",
    "(self-titled)", "[self-titled]", "s/t", "st", "homonimo"
]

def iniciar_driver():
    options = Options()
    options.add_argument("--headless") 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    driver = webdriver.Chrome(options=options)
    return driver

def login_spam(driver, user, password, wait_time=10):
    try:
        driver.get("https://spammusic.netlify.app/disc-list")
        wait = WebDriverWait(driver, wait_time)
        
        inputs = driver.find_elements(By.XPATH, "//input[@type='text' or @type='email']")
        if inputs:
            input_user = inputs[0]
            input_pass = driver.find_element(By.XPATH, "//input[@type='password']")
            
            input_user.clear()
            input_user.send_keys(user)
            input_pass.clear()
            input_pass.send_keys(password)
            input_pass.send_keys(Keys.RETURN)
            time.sleep(2) 
            driver.get("https://spammusic.netlify.app/disc-list")
            return True
        return True
    except Exception as e:
        print(f"Error en login: {e}")
        return False

def buscar_en_web(driver, termino, espera=3):
    try:
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Buscar álbum o artista...']"))
        )
        
        search_input.clear()
        search_input.send_keys(Keys.CONTROL + "a")
        search_input.send_keys(Keys.DELETE)
        search_input.send_keys(termino)
        
        time.sleep(0.1)
        search_input.send_keys(" ")
        time.sleep(0.1)
        search_input.send_keys(Keys.BACKSPACE)
        
        time.sleep(espera)
        
        cards = driver.find_elements(By.CLASS_NAME, "card")
        return len(cards) > 0
    except Exception:
        return False

def ejecutar_checker(lista_discos, user, password, genero_default="", callback_progress=None):
    faltantes = []
    total = len(lista_discos)
    
    print("🚀 Iniciando checker (modo headless)...")
    driver = iniciar_driver()
    
    try:
        if not login_spam(driver, user, password):
            print("❌ Fallo en el login.")
            return []
        
        for i, disco in enumerate(lista_discos):
            artista = disco.get('Artista', '').strip()
            album = disco.get('Álbum', '').strip()
            
            if callback_progress:
                callback_progress(i + 1, total, album)

            if "split" in album.lower():
                continue

            termino = album
            es_self_titled = album.lower().strip() in VARIACIONES_SELF_TITLED
            if es_self_titled:
                termino = artista
            
            encontrado = buscar_en_web(driver, termino)
            
            if not encontrado:
                print(f"   ❌ FALTA: {album}")
                genero_final = disco.get('Género') if disco.get('Género') not in ["N/A", ""] else genero_default
                
                faltantes.append({
                    'Artista': artista,
                    'Álbum': album,
                    'Género': genero_final,
                    'Fecha': disco.get('Fecha', ''),
                    'Spotify URL': disco.get('Spotify URL', '')
                })
                
    except Exception as e:
        print(f"💥 Error crítico: {e}")
    finally:
        driver.quit()
        
    return faltantes
