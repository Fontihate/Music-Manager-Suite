# 🎵 Music Data Scraper (AlbumOfTheYear)

<p align="left">
  <img src="https://img.shields.io/badge/python-3.x-blue.svg?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/github/stars/Fontihate/music-data-scraper?style=for-the-badge&color=gold" />
  <img src="https://img.shields.io/github/license/Fontihate/music-data-scraper?style=for-the-badge&color=green" />
  <img src="https://img.shields.io/github/issues/Fontihate/music-data-scraper?style=for-the-badge&color=red" />
</p>

---

**Music Data Scraper** es una herramienta potente y automatizada diseñada para recolectar metadatos musicales de la plataforma **AlbumOfTheYear**. Ideal para melómanos, analistas de datos o desarrolladores que buscan crear bases de datos musicales personalizadas de forma eficiente.

---

## 🛠️ Stack Tecnológico

| Herramienta | Función |
|---|---|
| **Python 3** | Motor principal del script. |
| **Cloudscraper** | Bypass avanzado para protecciones de seguridad (Cloudflare). |
| **BeautifulSoup4** | Procesamiento y limpieza del HTML extraído. |
| **CSV & Time** | Estructuración de datos y gestión de tiempos de espera. |

---

## 🚀 Funcionalidades Principales

| Categoría | Descripción |
|---|---|
| **Extracción Completa** | Obtiene Artista, Álbum, Género, Fecha y Enlace a Spotify. |
| **Paginación Inteligente** | Navega automáticamente por múltiples páginas de resultados. |
| **Antibaneo** | Implementa pausas aleatorias para simular comportamiento humano. |
| **Formateo de Datos** | Traduce y estructura fechas automáticamente al español. |

---

## 📦 Instalación

Sigue estos pasos para configurar el entorno localmente:

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/Fontihate/music-data-scraper.git
   cd music-data-scraper
   ```

2. **Instala las dependencias necesarias:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 📖 Modo de Uso

Para iniciar el proceso de extracción de datos, ejecuta el script principal desde tu terminal:

```bash
python rym_screaper.py
```

> [!TIP]
> Asegúrate de tener una conexión estable a internet. El script te guiará para introducir la URL o el género que deseas analizar.

---

## 📈 Roadmap de Desarrollo

- [ ] Soporte para múltiples géneros en una sola ejecución.
- [ ] Integración con la API de Spotify para metadatos extendidos.
- [ ] Exportación a formato JSON y bases de datos SQL.
- [ ] Creación de una interfaz gráfica (GUI) minimalista.

---

## 🤝 Cómo Contribuir

¡Las contribuciones son bienvenidas! Si quieres mejorar el proyecto, sigue estos pasos:

1. Haz un **Fork** del proyecto.
2. Crea una rama para tu mejora (`git checkout -b feature/MejoraIncreible`).
3. Realiza tus cambios y haz un **Commit** (`git commit -m 'Añadir MejoraIncreible'`).
4. Sube tus cambios a GitHub (`git push origin feature/MejoraIncreible`).
5. Abre un **Pull Request**.

---

Hecho con ❤️ por [Fontihate](https://github.com/Fontihate)
