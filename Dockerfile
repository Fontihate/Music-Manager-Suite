# Usamos una imagen base de Python ligera (Debian Bullseye)
FROM python:3.10-slim-bullseye

# 1. Instalamos dependencias del sistema y CHROMIUM (para Selenium)
# Esto es clave: en lugar de instalar Chrome "oficial", instalamos Chromium
# que es más ligero y funciona perfecto en servidores sin interfaz gráfica.
RUN apt-get update && apt-get install -y \
    chromium-driver \
    chromium \
    && rm -rf /var/lib/apt/lists/*

# 2. Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# 3. Copiamos el archivo de requisitos y las instalamos
# Hacemos esto primero para que Docker lo cachee y no lo reinstale cada vez que cambies una línea de código
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiamos el resto de archivos del proyecto
COPY . .

# 5. Configuramos variables de entorno
# Esto le dice a Selenium dónde está el ejecutable de Chrome
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# 6. Exponemos el puerto 8501 (El que usa Streamlit por defecto)
EXPOSE 8501

# 7. Comando para arrancar la aplicación
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
