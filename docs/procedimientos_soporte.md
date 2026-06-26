# Procedimientos de Soporte Técnico y Preguntas Frecuentes

## 1. Procedimientos de Soporte

### 1.1 Apertura de Ticket de Soporte

Para abrir un ticket de soporte técnico, el usuario debe seguir los siguientes pasos:

1. Acceder al portal de soporte en: http://soporte.empresa.interno
2. Iniciar sesión con credenciales corporativas.
3. Hacer clic en "Nuevo Ticket" en el panel principal.
4. Completar el formulario con la siguiente información:
   - **Título:** Descripción breve del problema (máximo 100 caracteres).
   - **Categoría:** Seleccionar entre Hardware, Software, Red, Servidor, Seguridad u Otro.
   - **Prioridad:** Baja, Media, Alta o Crítica según el impacto.
   - **Descripción detallada:** Incluir pasos para reproducir el problema, mensajes de error y cualquier cambio reciente realizado.
   - **Adjuntos:** Captura de pantalla o logs relevantes.
5. Hacer clic en "Enviar Ticket".

El sistema asignará automáticamente un número de ticket y enviará confirmación por correo electrónico.

### 1.2 Niveles de Prioridad

**Prioridad Crítica:**
- Servicio o sistema completamente caído que afecta a múltiples usuarios.
- Pérdida de datos en producción.
- Brecha de seguridad activa.
- Tiempo de respuesta: Inmediato (15 minutos).

**Prioridad Alta:**
- Funcionalidad importante no disponible que afecta el trabajo de un área.
- Degradación significativa del rendimiento.
- Tiempo de respuesta: 2 horas.

**Prioridad Media:**
- Problema que afecta a un usuario o grupo pequeño.
- Existe una alternativa temporal disponible.
- Tiempo de respuesta: 8 horas hábiles.

**Prioridad Baja:**
- Solicitudes de información o consultas generales.
- Mejoras o solicitudes no urgentes.
- Tiempo de respuesta: 3 días hábiles.

### 1.3 Seguimiento de Ticket

Los estados disponibles para un ticket son:
- **Abierto:** Ticket recibido, pendiente de asignación.
- **En Progreso:** Asignado a un técnico, en análisis.
- **En Espera:** Esperando respuesta del usuario o de un proveedor.
- **Resuelto:** Solución aplicada, pendiente confirmación del usuario.
- **Cerrado:** Problema confirmado como resuelto.

El usuario puede revisar el estado de su ticket en cualquier momento desde el portal de soporte o consultando el número de ticket en la línea de atención: interno 4500.

### 1.4 Escalamiento de Tickets

Si un ticket no es resuelto en el tiempo estipulado, se escala automáticamente:
- Nivel 1 → Nivel 2: Si no hay respuesta en el doble del tiempo de respuesta prometido.
- Nivel 2 → Nivel 3 (Jefatura): Si el tiempo supera el triple del tiempo prometido.

El usuario también puede solicitar escalamiento manual contactando al supervisor de soporte al interno 4501.

## 2. Procedimiento de Acceso Remoto

### 2.1 Conexión VPN

Para conectarse a la red interna desde fuera de la empresa:

1. Descargar el cliente VPN desde: http://it.empresa.interno/vpn
2. Instalar el cliente en el equipo.
3. Configurar con los siguientes parámetros:
   - Servidor: vpn.empresa.cl
   - Puerto: 443
   - Protocolo: SSL/TLS
4. Ingresar usuario y contraseña corporativos.
5. Aceptar la autenticación de doble factor (MFA).

### 2.2 Escritorio Remoto

Para soporte remoto de escritorio:
1. El usuario debe autorizar la conexión desde el portal de soporte.
2. El técnico iniciará la sesión usando el ticket activo.
3. Toda sesión remota queda registrada en el sistema de auditoría.

## 3. Procedimientos de Contraseñas

### 3.1 Política de Contraseñas

Las contraseñas corporativas deben cumplir:
- Mínimo 12 caracteres.
- Al menos una mayúscula, una minúscula, un número y un símbolo especial.
- No reutilizar las últimas 10 contraseñas.
- Vigencia máxima: 90 días.

### 3.2 Restablecimiento de Contraseña

**Por autoservicio:**
1. Acceder a: http://password.empresa.interno
2. Ingresar el correo corporativo.
3. Responder las preguntas de seguridad o usar el código enviado al correo de respaldo.
4. Establecer nueva contraseña.

**Por soporte:**
Si el autoservicio falla, abrir ticket de prioridad Alta indicando "Restablecimiento de contraseña" en el título.

## 4. Preguntas Frecuentes (FAQ)

### 4.1 Conectividad y Red

**¿Por qué no puedo conectarme a internet?**
Verificar en orden:
1. Comprobar que el cable de red está conectado o que el WiFi está habilitado.
2. Ejecutar `ping 8.8.8.8` para verificar conectividad básica.
3. Ejecutar `ping google.com` para verificar resolución DNS.
4. Si hay internet pero no acceso a sistemas internos, verificar la VPN.
5. Reiniciar adaptador de red: `sudo systemctl restart NetworkManager` en Linux.
6. Si persiste, abrir ticket de soporte con la salida de los comandos anteriores.

**¿Cómo liberar y renovar IP?**
En Linux:
```
sudo dhclient -r && sudo dhclient
```

**¿Cómo verificar la configuración DNS?**
```
cat /etc/resolv.conf
nslookup google.com
dig google.com
```

### 4.2 Servidores y Servicios

**¿Cómo verificar si un servidor está respondiendo?**
```
ping servidor
telnet servidor puerto
curl -I http://servidor
```

**¿Cómo reiniciar un servicio web en Linux?**
```
sudo systemctl restart nginx
sudo systemctl restart apache2
```

**¿Cómo verificar el espacio en disco de un servidor?**
```
df -h
du -sh /var/log/*   # Para identificar archivos de log grandes
```

**¿Cómo ver los logs del sistema en Linux?**
```
sudo journalctl -n 100           # Últimas 100 líneas del log del sistema
sudo journalctl -u nombre_servicio -n 50   # Logs de un servicio
sudo tail -f /var/log/syslog     # Log general en tiempo real
sudo tail -f /var/log/auth.log   # Log de autenticación
```

### 4.3 Gestión de Usuarios

**¿Cómo crear un nuevo usuario en el sistema?**
Debe abrir un ticket de soporte con la categoría "Gestión de Usuarios" indicando:
- Nombre completo del usuario.
- Cargo y área.
- Sistemas a los que necesita acceso.
- Fecha de inicio.
- Aprobación del jefatura directa adjunta.

**¿Cómo bloquear acceso de un usuario que se desvinculó?**
Contactar inmediatamente al soporte técnico con prioridad Alta. La deshabilitación de cuentas debe realizarse dentro de las 4 horas posteriores a la desvinculación.

**¿Cómo solicitar acceso a un sistema adicional?**
Abrir ticket indicando el sistema requerido. Se necesitará aprobación del responsable del sistema o jefatura.

### 4.4 Copias de Seguridad (Backup)

**¿Con qué frecuencia se realizan los backups?**
- Backup incremental: Diario a las 23:00 horas.
- Backup completo: Semanal los domingos a las 01:00 horas.
- Backup mensual: Primer día de cada mes.

**¿Cómo solicitar restauración de archivos?**
Abrir ticket indicando:
- Ruta exacta del archivo o directorio a restaurar.
- Fecha aproximada de la última versión correcta.
- Motivo de la restauración.

**¿Cuánto tiempo se conservan los backups?**
- Backups diarios: 30 días.
- Backups semanales: 3 meses.
- Backups mensuales: 1 año.

### 4.5 Software y Licencias

**¿Cómo solicitar instalación de software?**
Abrir ticket indicando:
- Nombre y versión del software.
- Justificación técnica.
- Equipo donde se instalará.

El software debe estar en la lista de aplicaciones aprobadas o pasar por un proceso de evaluación de seguridad antes de su instalación.

**¿Qué hacer si aparece un error de licencia?**
Abrir ticket con categoría "Software" adjuntando captura del mensaje de error. No intentar desactivar o modificar la licencia por cuenta propia.

### 4.6 Seguridad

**¿Qué hacer si sospecho de un virus o malware?**
1. Desconectar el equipo de la red inmediatamente (quitar cable o desactivar WiFi).
2. NO apagar el equipo para preservar evidencia.
3. Llamar inmediatamente a soporte: interno 4500 indicando "Incidente de Seguridad".
4. Abrir ticket con prioridad Crítica.

**¿Qué hacer si recibo un correo sospechoso (phishing)?**
1. No hacer clic en ningún enlace ni descargar adjuntos.
2. No responder el correo.
3. Reenviar el correo como adjunto a: seguridad@empresa.cl
4. Eliminar el correo de tu bandeja de entrada.

**¿Cómo reportar una vulnerabilidad de seguridad?**
Enviar un correo a seguridad@empresa.cl con:
- Descripción de la vulnerabilidad.
- Sistemas afectados.
- Impacto potencial.
- Pasos para reproducirla.

## 5. Mantenimiento Programado

Los mantenimientos se notifican con al menos 72 horas de anticipación vía correo electrónico y aviso en el portal de soporte.

**Ventanas de mantenimiento habituales:**
- Miércoles entre 22:00 y 02:00 horas: Actualizaciones de seguridad.
- Sábados entre 08:00 y 14:00 horas: Mantenimientos mayores.

Durante el mantenimiento, los servicios pueden estar no disponibles. Los usuarios deben planificar su trabajo considerando estas ventanas.
