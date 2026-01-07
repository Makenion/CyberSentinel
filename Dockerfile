# Usamos una imagen ligera de Python para optimizar recursos
FROM python:3.11-slim

# Evitamos que Python genere archivos .pyc y forzamos logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos primero el archivo que ya tienes listo
COPY requirements.txt .

# Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código del proyecto
COPY . .

# Creamos las carpetas de persistencia para que no den error
RUN mkdir -p logs data

# El comando para iniciar tu servicio automatizado del Día 6
CMD ["python", "main.py"]