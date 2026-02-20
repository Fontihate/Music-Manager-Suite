# 🎵 Music Manager Suite

![Python](https://img.shields.io/badge/python-3.10+-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-Headless-43B02A?style=for-the-badge&logo=selenium&logoColor=white)
![Cloudscraper](https://img.shields.io/badge/Cloudscraper-Bypass-orange?style=for-the-badge&logo=cloudflare&logoColor=white)

Suite integral para la gestión, extracción y verificación de catálogos musicales. Combina scraping avanzado de **AlbumOfTheYear**, automatización web con **Selenium** y enriquecimiento de metadatos vía **MusicBrainz API**. Diseñado para ser visual, modular y resistente a fallos de conexión.

---

## ✨ Características Principales

*   🖥️ **Interfaz Web Incluida**: Panel de control visual con Streamlit para gestionar el flujo de trabajo (Scrapear -> Verificar -> Corregir) sin tocar la terminal.
*   🎯 **Scraper Multifiltro**: Selección dinámica de Año, Mes, Género y Tipo de Release (LP, EP, etc.). Carga automáticamente los géneros disponibles en AOTY para el mes seleccionado.
*   🔍 **Verificador Automático**: Utiliza **Selenium** en modo Headless para cotejar tus discos con una base de datos externa (SpamMusic). Detecta "Self-Titled" y filtra "Splits" automáticamente.
*   🧠 **Enriquecimiento Inteligente**: Conecta con **MusicBrainz API** para rellenar países de origen y limpiar géneros. Prioriza los datos de AOTY y usa MusicBrainz como respaldo.
*   ⚡ **Lógica de Reintentos**: Sistema robusto que reintenta conexiones fallidas (Connection Aborted) automáticamente, garantizando que el proceso no se detenga.
*   📝 **Editor Manual**: Editor de tablas integrado (tipo Excel) dentro de la web para corregir manualmente los datos finales antes de exportar.

---

## 🛠️ Instalación y Requisitos

### 1. Requisitos Previos
*   **Python 3.10+**: Versión recomendada.
*   **Chrome/Chromium**: Navegador necesario para el módulo de verificación (Selenium).
*   **Driver de Chrome**: Asegúrate de tener una versión compatible de ChromeDriver en tu PATH (o usa el gestor automático de Selenium).

### 2. Clonar e Instalar
Clona el repositorio e instala las dependencias:

1.  `git clone https://github.com/tu_usuario/music-manager-suite.git`
2.  `cd music-manager-suite`
3.  `pip install -r requirements.txt`

---

## 🚀 Guía de Uso

El flujo de trabajo está diseñado para usarse a través de la **Interfaz Web**.

### Interfaz Web (Streamlit) 🌟
La forma más visual y sencilla de usar la herramienta.

1.  Ejecuta el comando: `streamlit run app.py`
2.  Se abrirá automáticamente una pestaña en tu navegador.
3.  **Paso 1 (Scraper)**: Selecciona filtros y extrae los datos. Los resultados se guardan en memoria.
4.  **Paso 2 (Checker)**: Coteja los resultados con tu colección externa para ver qué falta.
5.  **Paso 3 (Enrichment)**: Usa el botón "MusicBrainz" para buscar países de origen y corrige manualmente la tabla final.

---

## 📁 Estructura del Proyecto

    ├── app.py                # 🌟 Interfaz Web Streamlit y lógica de UI
    ├── aoty_screaper.py      # Módulo de scraping para AOTY (Cloudscraper)
    ├── checker_discos.py     # Módulo de automatización (Selenium Headless)
    ├── requirements.txt      # Dependencias del proyecto
    └── .env                  # Almacena tus credenciales (Local - Ignorado por Git)

---

## ⚙️ Detalles Técnicos y Optimización

*   **Resistencia a Errores**: Implementa un bucle de reintentos (`while` loop) para las peticiones a MusicBrainz, solucionando errores comunes como `ConnectionAbortedError` o `RemoteDisconnected`.
*   **Carga Dinámica**: El scraper no usa una lista de géneros hardcodeada; scrapea la URL del mes seleccionado para extraer los géneros *exactos* que tienen releases en ese periodo.
*   **Enlaces Inteligentes**: Detecta automáticamente enlaces de Spotify y Bandcamp. Si un álbum no tiene ninguno de los dos, es descartado automáticamente durante el scraping para mantener la lista limpia.
*   **User-Agent Ético**: Configuración personalizada de User-Agent para MusicBrainz, respetando sus normas de uso y evitando bloqueos.

---

## ⚠️ Seguridad y Privacidad
Este proyecto utiliza un archivo `.env` para las credenciales. 
**NUNCA SUBAS ESTE ARCHIVO A GITHUB NI A NINGÚN REPOSITORIO PÚBLICO.** 

El proyecto debe incluir un archivo `.gitignore` configurado para ignorar automáticamente:
*   `.env`
*   `discos_faltantes.csv`
*   `__pycache__/`

---

## 👨‍💻 Autor
Hecho con ❤️ por [Fontihate](https://github.com/Fontihate)

---
¡Si este proyecto te ha ahorrado tiempo, dale una ⭐ en GitHub!
