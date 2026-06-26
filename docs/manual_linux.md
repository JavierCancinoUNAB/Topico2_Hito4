# Manual de Linux - Soporte Técnico Interno

## 1. Introducción

Linux es un sistema operativo de código abierto basado en Unix. Es ampliamente utilizado en servidores, sistemas embebidos y estaciones de trabajo de desarrollo. Este manual cubre los comandos y procedimientos más utilizados en el soporte técnico diario.

## 2. Gestión de Archivos y Directorios

### 2.1 Navegación

**Ver directorio actual:**
```
pwd
```

**Listar contenido de un directorio:**
```
ls
ls -l       # Formato largo con permisos, tamaño y fecha
ls -la      # Incluye archivos ocultos
ls -lh      # Tamaños legibles (KB, MB, GB)
```

**Cambiar de directorio:**
```
cd /ruta/al/directorio
cd ..       # Subir un nivel
cd ~        # Ir al directorio home del usuario
cd -        # Volver al directorio anterior
```

### 2.2 Operaciones con Archivos

**Crear archivo vacío:**
```
touch nombre_archivo.txt
```

**Crear directorio:**
```
mkdir nombre_directorio
mkdir -p ruta/completa/de/directorios    # Crea directorios intermedios
```

**Copiar archivos:**
```
cp origen destino
cp -r directorio_origen directorio_destino    # Copia recursiva de directorios
```

**Mover/Renombrar archivos:**
```
mv origen destino
```

**Eliminar archivos:**
```
rm nombre_archivo
rm -r nombre_directorio    # Elimina directorio y contenido recursivamente
rm -rf nombre_directorio   # Fuerza eliminación sin confirmación (¡CUIDADO!)
```

**Ver contenido de archivos:**
```
cat archivo.txt             # Muestra todo el contenido
head -n 20 archivo.txt     # Muestra las primeras 20 líneas
tail -n 20 archivo.txt     # Muestra las últimas 20 líneas
tail -f archivo.log        # Monitorea el archivo en tiempo real
less archivo.txt            # Visualización paginada (q para salir)
```

**Buscar archivos:**
```
find /ruta -name "nombre_archivo"
find /home -name "*.log"              # Busca todos los archivos .log
find /var -size +100M                 # Archivos mayores a 100MB
```

**Buscar texto dentro de archivos:**
```
grep "texto_buscado" archivo.txt
grep -r "texto_buscado" /directorio   # Búsqueda recursiva
grep -i "texto"  archivo.txt          # Búsqueda sin distinción de mayúsculas
grep -n "texto" archivo.txt           # Muestra número de línea
```

## 3. Gestión de Procesos

**Visualizar procesos en ejecución:**
```
ps aux          # Lista todos los procesos del sistema
ps aux | grep nombre_proceso    # Filtrar por nombre
```

**Monitor de procesos en tiempo real:**
```
top             # Monitor básico
htop            # Monitor mejorado (requiere instalación)
```

**Terminar un proceso:**
```
kill PID                    # Envía señal SIGTERM (terminación ordenada)
kill -9 PID                 # Envía SIGKILL (terminación forzada)
killall nombre_proceso      # Termina todos los procesos con ese nombre
pkill nombre_proceso        # Similar a killall
```

**Ejecutar proceso en segundo plano:**
```
comando &
```

**Ver jobs en segundo plano:**
```
jobs
```

**Traer proceso al primer plano:**
```
fg %número_job
```

## 4. Permisos y Propietarios

### 4.1 Entendiendo los Permisos

Los permisos en Linux tienen tres niveles:
- **Propietario (u):** el usuario dueño del archivo
- **Grupo (g):** el grupo al que pertenece el archivo
- **Otros (o):** el resto de usuarios

Tipos de permisos:
- **r (4):** lectura
- **w (2):** escritura
- **x (1):** ejecución

### 4.2 Cambiar Permisos

**Con notación octal:**
```
chmod 755 archivo       # rwxr-xr-x
chmod 644 archivo       # rw-r--r--
chmod 777 archivo       # rwxrwxrwx (¡evitar en producción!)
chmod -R 755 directorio # Aplica recursivamente
```

**Con notación simbólica:**
```
chmod u+x archivo       # Agrega ejecución al propietario
chmod g-w archivo       # Quita escritura al grupo
chmod o+r archivo       # Agrega lectura a otros
chmod a+x archivo       # Agrega ejecución a todos
```

### 4.3 Cambiar Propietario

```
chown usuario archivo
chown usuario:grupo archivo
chown -R usuario:grupo directorio    # Aplica recursivamente
```

## 5. Gestión de Usuarios y Grupos

**Crear usuario:**
```
sudo useradd -m -s /bin/bash nombre_usuario
sudo passwd nombre_usuario
```

**Eliminar usuario:**
```
sudo userdel nombre_usuario
sudo userdel -r nombre_usuario    # Elimina también el directorio home
```

**Modificar usuario:**
```
sudo usermod -aG grupo nombre_usuario    # Agregar a un grupo
sudo usermod -s /bin/bash usuario        # Cambiar shell
```

**Crear grupo:**
```
sudo groupadd nombre_grupo
```

**Ver información del usuario actual:**
```
whoami
id
groups
```

**Cambiar a otro usuario:**
```
su nombre_usuario
sudo su -        # Cambiar a root
```

## 6. Gestión de Paquetes

### Ubuntu/Debian (APT):
```
sudo apt-get update                      # Actualizar lista de paquetes
sudo apt-get upgrade                     # Actualizar paquetes instalados
sudo apt-get install nombre_paquete      # Instalar paquete
sudo apt-get remove nombre_paquete       # Desinstalar paquete
sudo apt-get autoremove                  # Eliminar dependencias no usadas
apt-cache search término                 # Buscar paquetes
```

### CentOS/RHEL (YUM/DNF):
```
sudo yum update
sudo yum install nombre_paquete
sudo yum remove nombre_paquete
sudo yum search término
```

## 7. Red y Conectividad

**Ver interfaces de red:**
```
ip addr show
ifconfig        # En sistemas más antiguos
```

**Ver tabla de rutas:**
```
ip route show
route -n
```

**Probar conectividad:**
```
ping destino
ping -c 4 google.com    # Envía solo 4 paquetes
```

**Ver puertos en uso:**
```
netstat -tulpn
ss -tulpn       # Alternativa más moderna
```

**Verificar conexiones activas:**
```
netstat -an
ss -an
```

**Transferir archivos:**
```
scp archivo usuario@servidor:/ruta/destino
scp -r directorio usuario@servidor:/ruta/destino
```

**Conexión SSH:**
```
ssh usuario@servidor
ssh -p 2222 usuario@servidor    # Puerto personalizado
```

## 8. Servicios y Systemd

**Ver estado de un servicio:**
```
sudo systemctl status nombre_servicio
```

**Iniciar un servicio:**
```
sudo systemctl start nombre_servicio
```

**Detener un servicio:**
```
sudo systemctl stop nombre_servicio
```

**Reiniciar un servicio:**
```
sudo systemctl restart nombre_servicio
```

**Habilitar inicio automático:**
```
sudo systemctl enable nombre_servicio
```

**Deshabilitar inicio automático:**
```
sudo systemctl disable nombre_servicio
```

**Listar todos los servicios:**
```
sudo systemctl list-units --type=service
```

## 9. Espacio en Disco

**Ver uso del disco:**
```
df -h           # Muestra uso por partición en formato legible
df -h /         # Solo para la partición raíz
```

**Ver tamaño de directorios:**
```
du -sh /ruta/directorio
du -sh *        # Tamaño de cada elemento en directorio actual
du -sh /* | sort -h    # Ordenado por tamaño
```

## 10. Variables de Entorno

**Ver variables de entorno:**
```
env
printenv
echo $VARIABLE
```

**Definir variable temporal:**
```
export MI_VARIABLE="valor"
```

**Definir variable permanente:**
Agregar al archivo `~/.bashrc` o `~/.profile`:
```
export MI_VARIABLE="valor"
```

Luego recargar:
```
source ~/.bashrc
```

## 11. Compresión y Archivos

**Crear archivo tar:**
```
tar -cvf archivo.tar directorio/
tar -czvf archivo.tar.gz directorio/    # Con compresión gzip
```

**Extraer archivo tar:**
```
tar -xvf archivo.tar
tar -xzvf archivo.tar.gz
tar -xzvf archivo.tar.gz -C /destino/  # En directorio específico
```

**Comprimir con zip:**
```
zip -r archivo.zip directorio/
unzip archivo.zip
```

## 12. Solución de Problemas Comunes

**Disco lleno:**
Identificar qué ocupa más espacio: `du -sh /* | sort -rh | head -20`

**Proceso que no responde:**
Obtener PID con `ps aux | grep proceso` y luego `kill -9 PID`

**Sin permisos de acceso:**
Verificar permisos con `ls -la` y ajustar con `chmod` o `chown`

**Servicio que no inicia:**
Revisar logs con `sudo journalctl -u nombre_servicio -n 50`

**Puerto bloqueado:**
Verificar firewall con `sudo ufw status` o `sudo iptables -L`
