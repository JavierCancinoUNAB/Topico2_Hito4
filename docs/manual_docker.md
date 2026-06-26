# Manual de Docker - Soporte Técnico Interno

## 1. Introducción a Docker

Docker es una plataforma de contenedores que permite empaquetar aplicaciones junto con sus dependencias en unidades aisladas llamadas contenedores. A diferencia de las máquinas virtuales, los contenedores comparten el kernel del sistema operativo anfitrión, lo que los hace más ligeros y eficientes.

## 2. Conceptos Fundamentales

### 2.1 Imagen Docker
Una imagen Docker es una plantilla de solo lectura que contiene el sistema de archivos y la configuración necesaria para ejecutar una aplicación. Las imágenes se construyen mediante un archivo llamado Dockerfile.

### 2.2 Contenedor
Un contenedor es una instancia en ejecución de una imagen Docker. Cada contenedor es un proceso aislado con su propio sistema de archivos, red y proceso.

### 2.3 Dockerfile
El Dockerfile es un archivo de texto que define los pasos para construir una imagen Docker. Cada instrucción en el Dockerfile crea una capa en la imagen.

### 2.4 Docker Hub
Docker Hub es el registro público de imágenes Docker. Permite descargar imágenes oficiales de aplicaciones como Nginx, MySQL, Python, entre otras.

### 2.5 Docker Compose
Docker Compose es una herramienta para definir y ejecutar aplicaciones multicontenedor. Utiliza un archivo YAML (docker-compose.yml) para configurar los servicios.

## 3. Instalación de Docker

### En Ubuntu/Debian:
```
sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

### En CentOS/RHEL:
```
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
```

## 4. Comandos Esenciales

### 4.1 Gestión de Imágenes

**Descargar una imagen:**
```
docker pull nombre_imagen:tag
```
Ejemplo: `docker pull nginx:latest`

**Listar imágenes locales:**
```
docker images
```

**Eliminar una imagen:**
```
docker rmi nombre_imagen:tag
```

**Crear una imagen desde un Dockerfile:**
```
docker build -t nombre_imagen:tag .
```
El punto (.) indica que el Dockerfile está en el directorio actual.

**Construir con un Dockerfile específico:**
```
docker build -f /ruta/Dockerfile -t nombre_imagen:tag .
```

### 4.2 Gestión de Contenedores

**Ejecutar un contenedor:**
```
docker run nombre_imagen
```

**Ejecutar un contenedor en modo interactivo:**
```
docker run -it nombre_imagen /bin/bash
```

**Ejecutar un contenedor en modo detached (segundo plano):**
```
docker run -d nombre_imagen
```

**Ejecutar con nombre personalizado:**
```
docker run --name mi_contenedor -d nombre_imagen
```

**Mapear puertos:**
```
docker run -p puerto_host:puerto_contenedor nombre_imagen
```
Ejemplo: `docker run -p 8080:80 nginx` mapea el puerto 80 del contenedor al 8080 del host.

**Montar volúmenes:**
```
docker run -v /ruta/host:/ruta/contenedor nombre_imagen
```

**Pasar variables de entorno:**
```
docker run -e VARIABLE=valor nombre_imagen
```

**Listar contenedores en ejecución:**
```
docker ps
```

**Listar todos los contenedores (incluyendo detenidos):**
```
docker ps -a
```

**Detener un contenedor:**
```
docker stop nombre_o_id_contenedor
```

**Iniciar un contenedor detenido:**
```
docker start nombre_o_id_contenedor
```

**Reiniciar un contenedor:**
```
docker restart nombre_o_id_contenedor
```

**Eliminar un contenedor:**
```
docker rm nombre_o_id_contenedor
```
Nota: El contenedor debe estar detenido para eliminarlo.

**Forzar eliminación de contenedor en ejecución:**
```
docker rm -f nombre_o_id_contenedor
```

**Acceder a un contenedor en ejecución:**
```
docker exec -it nombre_contenedor /bin/bash
```

### 4.3 Logs y Monitoreo

**Ver logs de un contenedor:**
```
docker logs nombre_contenedor
```

**Ver logs en tiempo real:**
```
docker logs -f nombre_contenedor
```

**Ver estadísticas de recursos:**
```
docker stats
```

**Inspeccionar detalles de un contenedor:**
```
docker inspect nombre_contenedor
```

## 5. Dockerfile - Guía de Instrucciones

### Instrucciones básicas:

- `FROM`: Define la imagen base. Siempre debe ser la primera instrucción.
- `RUN`: Ejecuta comandos durante la construcción de la imagen.
- `COPY`: Copia archivos desde el host hacia la imagen.
- `ADD`: Similar a COPY, pero también soporta URLs y descompresión de archivos tar.
- `WORKDIR`: Establece el directorio de trabajo dentro del contenedor.
- `ENV`: Define variables de entorno.
- `EXPOSE`: Documenta los puertos que usará el contenedor (no los publica).
- `CMD`: Define el comando por defecto al iniciar el contenedor.
- `ENTRYPOINT`: Define el ejecutable principal del contenedor.

### Ejemplo de Dockerfile para aplicación Python:
```
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

## 6. Docker Compose

### Estructura básica de docker-compose.yml:
```yaml
version: '3.8'
services:
  web:
    image: nginx:latest
    ports:
      - "8080:80"
    volumes:
      - ./html:/usr/share/nginx/html
  
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: secreto
      MYSQL_DATABASE: mi_base
    volumes:
      - db_data:/var/lib/mysql

volumes:
  db_data:
```

### Comandos de Docker Compose:

**Iniciar servicios:**
```
docker-compose up
```

**Iniciar en modo detached:**
```
docker-compose up -d
```

**Detener servicios:**
```
docker-compose down
```

**Ver logs:**
```
docker-compose logs -f
```

**Reconstruir imágenes:**
```
docker-compose build
```

## 7. Redes en Docker

**Listar redes:**
```
docker network ls
```

**Crear red personalizada:**
```
docker network create mi_red
```

**Conectar contenedor a una red:**
```
docker network connect mi_red nombre_contenedor
```

**Ejecutar contenedor en red específica:**
```
docker run --network=mi_red nombre_imagen
```

## 8. Volúmenes

Los volúmenes permiten persistir datos más allá del ciclo de vida de un contenedor.

**Crear volumen:**
```
docker volume create mi_volumen
```

**Listar volúmenes:**
```
docker volume ls
```

**Eliminar volumen:**
```
docker volume rm mi_volumen
```

**Usar volumen en contenedor:**
```
docker run -v mi_volumen:/datos nombre_imagen
```

## 9. Limpieza del Sistema

**Eliminar contenedores detenidos:**
```
docker container prune
```

**Eliminar imágenes sin uso:**
```
docker image prune
```

**Eliminar todo lo no utilizado (contenedores, redes, imágenes):**
```
docker system prune
```

**Eliminación completa incluyendo volúmenes:**
```
docker system prune -a --volumes
```

## 10. Solución de Problemas Comunes

**El contenedor se detiene inmediatamente:**
Verificar los logs con `docker logs nombre_contenedor` para identificar el error.

**Puerto ya en uso:**
Error "port is already allocated". Cambiar el puerto del host o detener el proceso que usa ese puerto.

**Imagen no encontrada:**
Verificar el nombre y tag de la imagen. Intentar con `docker pull` para descargar la imagen.

**Permisos denegados:**
Asegurarse de que el usuario esté en el grupo docker: `sudo usermod -aG docker $USER` y luego cerrar y abrir sesión.
