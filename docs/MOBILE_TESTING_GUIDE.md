# 📱 Guía de Pruebas con Teléfono Móvil

Guía completa para probar el sistema de detecciones usando tu teléfono como cámara.

## 🎯 Objetivo

Usar tu teléfono móvil conectado por USB (o WiFi) para tomar fotos y enviarlas al backend, simulando el comportamiento de una cámara Hikvision.

---

## 📋 Requisitos Previos

1. ✅ Backend corriendo en tu PC
2. ✅ Teléfono y PC en la misma red WiFi (o conectado por USB)
3. ✅ Navegador web en el teléfono
4. ✅ Base de datos con ubicaciones y cámaras creadas

---

## 🚀 Configuración Paso a Paso

### Paso 1: Preparar el Backend

```bash
# 1. Aplicar migraciones
alembic upgrade head

# 2. Iniciar el servidor
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Importante:** Usa `--host 0.0.0.0` para que el servidor sea accesible desde otros dispositivos en la red.

### Paso 2: Obtener la IP de tu PC

#### Windows:

```bash
ipconfig
```

Busca "Dirección IPv4" (ejemplo: `192.168.1.100`)

#### Linux/Mac:

```bash
ifconfig
# o
ip addr show
```

### Paso 3: Configurar CORS (si es necesario)

El archivo `app/main.py` ya tiene CORS configurado para permitir todas las conexiones:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Paso 4: Crear Ubicación y Cámara de Prueba

Usa Postman o cURL para crear los datos necesarios:

```bash
# 1. Login para obtener token
curl -X POST "http://localhost:8000/auth/jwt/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin123"

# 2. Crear ubicación
curl -X POST "http://localhost:8000/ubicaciones" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ubicacion_id": "ubicacion_test_001",
    "name": "Ubicación de Prueba Móvil",
    "description": "Para pruebas con teléfono",
    "location": "Casa/Oficina",
    "is_active": true
  }'

# 3. Crear cámara (simula tu teléfono)
curl -X POST "http://localhost:8000/cameras" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "mac": "AA:BB:CC:DD:EE:01",
    "name": "Teléfono Móvil - Test",
    "model": "Smartphone Camera",
    "ip_address": "192.168.1.XXX",
    "orientacion": "Frontal",
    "ubicacion_id": 1,
    "is_active": true
  }'
```

---

## 📱 Opción 1: Usar la App Web HTML

### Abrir la App en el Móvil

1. **Abre el archivo HTML en tu PC:**

   - Navega a: `c:\Users\isaac\Documents\GitHub\Odin\mobile_test_app.html`
   - Haz doble clic para abrirlo en el navegador

2. **Obtén la URL local:**

   - Si usas un servidor local simple:

   ```bash
   # En la carpeta del proyecto
   python -m http.server 8080
   ```

   - URL: `http://TU_IP_PC:8080/mobile_test_app.html`

3. **Abre en el móvil:**
   - En el navegador del teléfono, ve a: `http://192.168.1.100:8080/mobile_test_app.html`
   - Reemplaza `192.168.1.100` con la IP de tu PC

### Usar la App

1. **Configurar:**

   - IP del Servidor: `192.168.1.100:8000`
   - ID de Ubicación: `ubicacion_test_001`
   - MAC Address: `AA:BB:CC:DD:EE:01`

2. **Tomar Foto:**

   - Toca "📸 Tomar/Seleccionar Foto"
   - Toma una foto con la cámara o selecciona una de la galería

3. **Enviar:**
   - Toca "🚀 Enviar Detección"
   - Espera la confirmación

---

## 📱 Opción 2: Usar cURL desde Terminal Móvil

Si tienes Termux (Android) o iSH (iOS):

```bash
curl -X POST "http://192.168.1.100:8000/detections/upload" \
  -F "ubicacion_id=ubicacion_test_001" \
  -F "mac=AA:BB:CC:DD:EE:01" \
  -F "image_path=/mobile/test.jpg" \
  -F "image=@/path/to/photo.jpg"
```

---

## 🔍 Verificar que Funcionó

### 1. Ver Detecciones en el Backend

```bash
# Obtener todas las detecciones
curl -X GET "http://localhost:8000/detections?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Ver detalles de una detección específica
curl -X GET "http://localhost:8000/detections/1/details" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. Ver Logs del Servidor

En la terminal donde corre uvicorn, deberías ver:

```
INFO: Imagen recibida: photo.jpg, tamaño: 245678 bytes
INFO: Detección creada: ID=1, Ubicación=ubicacion_test_001, MAC=AA:BB:CC:DD:EE:01
```

### 3. Verificar en la Base de Datos

```sql
SELECT * FROM detections ORDER BY created_at DESC LIMIT 5;
SELECT * FROM cameras WHERE mac = 'AA:BB:CC:DD:EE:01';
```

---

## 🐛 Solución de Problemas

### Error: "No se puede conectar"

**Causa:** El móvil no puede alcanzar el servidor.

**Solución:**

1. Verifica que ambos dispositivos estén en la misma red WiFi
2. Desactiva el firewall de Windows temporalmente:
   ```bash
   # PowerShell como Administrador
   Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False
   ```
3. O agrega una regla de firewall para el puerto 8000:
   ```bash
   netsh advfirewall firewall add rule name="FastAPI" dir=in action=allow protocol=TCP localport=8000
   ```

### Error: "Ubicación no encontrada"

**Causa:** La ubicación o cámara no existen en la BD.

**Solución:**

1. Verifica que creaste la ubicación y cámara
2. Usa los IDs correctos en la app móvil
3. Verifica en la BD:
   ```sql
   SELECT * FROM ubicaciones;
   SELECT * FROM cameras;
   ```

### Error: "CORS"

**Causa:** El navegador bloquea la petición.

**Solución:**

- Ya está configurado en `app/main.py`
- Si persiste, reinicia el servidor

### La imagen no se guarda

**Causa:** El endpoint recibe la imagen pero no la guarda en disco.

**Solución:**

- Por ahora, la imagen se recibe pero no se guarda automáticamente
- Puedes implementar el guardado en `app/detections/routes.py`:

```python
# En upload_detection_from_camera
if image_data:
    # Guardar imagen en disco
    import os
    from datetime import datetime

    upload_dir = "uploads/detections"
    os.makedirs(upload_dir, exist_ok=True)

    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{ubicacion_id}.jpg"
    filepath = os.path.join(upload_dir, filename)

    with open(filepath, 'wb') as f:
        f.write(image_data)

    # Actualizar detection con la ruta real
    detection.image_path = filepath
    await db.commit()
```

---

## 📊 Flujo Completo de Prueba

```
1. PC: Iniciar backend
   uvicorn app.main:app --host 0.0.0.0 --port 8000

2. PC: Crear ubicación y cámara (Postman)
   POST /ubicaciones
   POST /cameras

3. Móvil: Abrir app web
   http://192.168.1.100:8080/mobile_test_app.html

4. Móvil: Configurar y tomar foto
   - Ingresar IP, ubicacion_id, MAC
   - Tomar foto
   - Enviar

5. PC: Verificar detección
   GET /detections
   GET /detections/1/details

6. PC: Ver logs
   INFO: Detección creada: ID=1...
```

---

## 🎨 Personalizar la App Móvil

El archivo `mobile_test_app.html` es completamente personalizable:

### Cambiar Colores

```css
/* En el <style> */
background: linear-gradient(135deg, #TU_COLOR_1 0%, #TU_COLOR_2 100%);
```

### Agregar Más Campos

```html
<div class="form-group">
  <label for="nuevocamp">🏷️ Nuevo Campo</label>
  <input type="text" id="nuevocampo" placeholder="Valor" />
</div>
```

### Cambiar el Logo

```html
<h1>🦅 Tu Logo Aquí</h1>
```

---

## 📝 Notas Importantes

1. **Seguridad:** Este método es solo para pruebas. En producción, deberías:

   - Usar HTTPS
   - Implementar autenticación para el endpoint de upload
   - Validar y sanitizar las imágenes

2. **Rendimiento:** Las imágenes de móvil pueden ser muy grandes (5-10 MB)

   - Considera comprimir las imágenes antes de enviar
   - Implementa límites de tamaño

3. **Almacenamiento:** Decide dónde guardar las imágenes:
   - Disco local (para pruebas)
   - Cloud storage (AWS S3, Google Cloud Storage)
   - Base de datos (no recomendado para imágenes grandes)

---

## 🚀 Próximos Pasos

Una vez que funcione con el móvil:

1. ✅ Integrar con tu modelo de IA
2. ✅ Implementar almacenamiento en cloud
3. ✅ Crear dashboard para visualizar detecciones
4. ✅ Configurar cámaras Hikvision reales
5. ✅ Implementar notificaciones en tiempo real

---

**¡Listo para probar!** 📱🚀

Si tienes problemas, revisa los logs del servidor y verifica la conectividad de red.
