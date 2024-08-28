# Usar una imagen base ligera de Python
FROM python:3.9-slim

RUN apt-get update

RUN apt-get install sqlite3

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos de la aplicación al contenedor
COPY . /app

# Instalar las dependencias necesarias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto en el que Flask estará corriendo
EXPOSE 5000

# Ejecutar el script de inicialización de la base de datos antes de iniciar el servidor
CMD ["python", "app.py"]

