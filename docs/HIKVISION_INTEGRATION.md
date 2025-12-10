# 📹 Integración con Cámaras Hikvision

## 🎯 Objetivo

Configurar cámaras Hikvision para que envíen automáticamente imágenes al backend cuando detecten movimiento o eventos.

## 🔧 Configuración de Cámara Hikvision

### 1. Acceder a la Interfaz Web

1. Abrir navegador: `http://IP_DE_LA_CAMARA`
2. Login con usuario/contraseña de la cámara
3. Ir a: **Configuration → Event → Smart Event**

### 2. Configurar HTTP Listening

#### Opción A: HTTP Notification (Recomendado)

1. Ir a: **Configuration → Network → Advanced Settings → HTTP Listening**
2. Habilitar: **Enable HTTP Listening**
3. Configurar:
   ```
   URL: http://TU_SERVIDOR_IP:8000/detections/upload
   Protocol Version: HTTP/1.1
   Method: POST
   ```

#### Opción B: FTP Upload

1. Ir a: **Configuration → Network → Advanced Settings → FTP**
2. Configurar servidor FTP
3. Crear script que monitoree carpeta FTP y envíe al backend

### 3. Configurar Detección de Eventos

#### Motion Detection (Detección de Movimiento)

1. Ir a: **Configuration → Event → Basic Event → Motion Detection**
2. Habilitar: **Enable Motion Detection**
3. Configurar áreas de detección (dibujar en la imagen)
4. Ajustar sensibilidad
5. En **Linkage Method**, seleccionar:
   - ✅ **Notify Surveillance Center**
   - ✅ **Upload to FTP/Memory Card/NAS**
   - ✅ **Send Email**

#### Line Crossing Detection (Cruce de Línea)

1. Ir a: **Configuration → Event → Smart Event → Line Crossing Detection**
2. Habilitar y dibujar línea
3. Configurar dirección (A→B, B→A, o ambas)
4. En **Linkage Method**, habilitar notificaciones

#### Intrusion Detection (Detección de Intrusión)

1. Ir a: **Configuration → Event → Smart Event → Intrusion Detection**
2. Dibujar área de detección
3. Configurar tiempo mínimo de permanencia
4. Habilitar notificaciones

## 📡 Formato de Datos de Hikvision

### Estructura XML Típica

Las cámaras Hikvision envían datos en formato XML:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<EventNotificationAlert version="2.0">
    <ipAddress>192.168.1.100</ipAddress>
    <portNo>80</portNo>
    <protocol>HTTP</protocol>
    <macAddress>AA:BB:CC:DD:EE:FF</macAddress>
    <channelID>1</channelID>
    <dateTime>2024-01-01T10:00:00+00:00</dateTime>
    <activePostCount>1</activePostCount>
    <eventType>linedetection</eventType>
    <eventState>active</eventState>
    <eventDescription>Line Crossing Detection</eventDescription>
    <DetectionRegionList>
        <DetectionRegionEntry>
            <regionID>1</regionID>
            <sensitivityLevel>50</sensitivityLevel>
        </DetectionRegionEntry>
    </DetectionRegionList>
</EventNotificationAlert>
```

## 🔄 Adaptador para Hikvision

Crear un endpoint específico para recibir notificaciones de Hikvision:

### `app/detections/routes.py` - Agregar endpoint:

```python
from fastapi import Request
import xml.etree.ElementTree as ET

@router.post("/hikvision/event", status_code=status.HTTP_200_OK)
async def receive_hikvision_event(
    request: Request,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Endpoint para recibir eventos de cámaras Hikvision

    Las cámaras Hikvision envían notificaciones en formato XML
    cuando detectan eventos (movimiento, cruce de línea, etc.)
    """
    try:
        # Leer body XML
        body = await request.body()
        xml_data = body.decode('utf-8')

        # Parsear XML
        root = ET.fromstring(xml_data)

        # Extraer datos
        mac_address = root.find('macAddress').text
        event_type = root.find('eventType').text
        date_time = root.find('dateTime').text
        ip_address = root.find('ipAddress').text

        logger.info(f"Evento Hikvision recibido: MAC={mac_address}, Type={event_type}")

        # Buscar cámara por MAC
        camera = await CameraService.get_camera_by_mac(db, mac_address)
        if not camera:
            logger.warning(f"Cámara no encontrada: {mac_address}")
            return {"success": False, "message": "Camera not found"}

        # Obtener snapshot de la cámara
        image_data = await capture_hikvision_snapshot(ip_address, camera.username, camera.password)

        # Crear detección
        detection_data = DetectionFromCamera(
            location_id=camera.location.location_id,
            mac=mac_address,
            image_path=f"hikvision_{event_type}_{date_time}.jpg"
        )

        detection = await DetectionService.create_detection_from_camera(
            db,
            detection_data,
            image_data
        )

        return {
            "success": True,
            "message": "Event received",
            "detection_id": detection.id
        }

    except Exception as e:
        logger.error(f"Error procesando evento Hikvision: {e}")
        return {"success": False, "message": str(e)}


async def capture_hikvision_snapshot(ip: str, username: str, password: str) -> bytes:
    """
    Capturar snapshot de cámara Hikvision

    URL típica: http://IP/ISAPI/Streaming/channels/101/picture
    """
    import aiohttp
    from aiohttp import BasicAuth

    url = f"http://{ip}/ISAPI/Streaming/channels/101/picture"

    async with aiohttp.ClientSession() as session:
        async with session.get(
            url,
            auth=BasicAuth(username, password),
            timeout=aiohttp.ClientTimeout(total=10)
        ) as response:
            if response.status == 200:
                return await response.read()
            else:
                raise Exception(f"Error capturando snapshot: {response.status}")
```

## 🔐 Seguridad

### Agregar Autenticación para Cámaras

En `app/cameras/models.py`, agregar campos:

```python
class Camera(Base):
    # ... campos existentes ...

    # Credenciales para acceder a la cámara
    username: Mapped[str] = mapped_column(String(50), nullable=True)
    password: Mapped[str] = mapped_column(String(100), nullable=True)

    # IP de la cámara
    ip_address: Mapped[str] = mapped_column(String(15), nullable=True)
```

### Validar Origen de Peticiones

```python
from fastapi import Header, HTTPException

async def verify_camera_origin(
    x_forwarded_for: str = Header(None),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Verificar que la petición viene de una cámara registrada
    """
    if not x_forwarded_for:
        raise HTTPException(status_code=403, detail="Origin not allowed")

    # Verificar que la IP está en la lista de cámaras
    camera = await CameraService.get_camera_by_ip(db, x_forwarded_for)
    if not camera:
        raise HTTPException(status_code=403, detail="Camera not registered")

    return camera
```

## 🧪 Testing

### Simular Evento de Hikvision

```python
import requests

xml_data = """<?xml version="1.0" encoding="UTF-8"?>
<EventNotificationAlert version="2.0">
    <ipAddress>192.168.1.100</ipAddress>
    <macAddress>AA:BB:CC:DD:EE:01</macAddress>
    <eventType>linedetection</eventType>
    <dateTime>2024-01-01T10:00:00+00:00</dateTime>
</EventNotificationAlert>"""

response = requests.post(
    "http://localhost:8000/detections/hikvision/event",
    data=xml_data,
    headers={"Content-Type": "application/xml"}
)

print(response.json())
```

### Capturar Snapshot Manualmente

```bash
curl -u admin:password "http://192.168.1.100/ISAPI/Streaming/channels/101/picture" \
  --output snapshot.jpg
```

## 📋 Checklist de Configuración

- [ ] Cámara conectada a la red
- [ ] IP fija asignada a la cámara
- [ ] Cámara registrada en la base de datos (MAC, IP, credenciales)
- [ ] HTTP Listening habilitado en la cámara
- [ ] URL del backend configurada en la cámara
- [ ] Eventos de detección habilitados
- [ ] Linkage Methods configurados
- [ ] Firewall permite conexión desde cámara al backend
- [ ] Backend accesible desde la red de la cámara
- [ ] Credenciales de cámara guardadas en BD

## 🔍 Troubleshooting

### Cámara no envía eventos

1. **Verificar conectividad:**

   ```bash
   ping IP_DE_LA_CAMARA
   ```

2. **Verificar que el backend es accesible desde la cámara:**

   - Desde la interfaz web de la cámara, hacer ping al servidor
   - Verificar que el puerto 8000 está abierto

3. **Revisar logs de la cámara:**

   - Configuration → System → Maintenance → Log
   - Buscar errores de HTTP Notification

4. **Verificar configuración de eventos:**
   - Asegurar que los eventos están habilitados
   - Verificar que las áreas de detección están bien configuradas
   - Ajustar sensibilidad si no detecta

### Backend no recibe eventos

1. **Verificar logs del backend:**

   ```bash
   # Ver logs en tiempo real
   tail -f logs/app.log
   ```

2. **Verificar endpoint:**

   ```bash
   curl -X POST http://localhost:8000/detections/hikvision/event \
     -H "Content-Type: application/xml" \
     -d '<EventNotificationAlert><macAddress>AA:BB:CC:DD:EE:01</macAddress></EventNotificationAlert>'
   ```

3. **Verificar firewall:**

   ```bash
   # Windows
   netsh advfirewall firewall add rule name="Odin API" dir=in action=allow protocol=TCP localport=8000

   # Linux
   sudo ufw allow 8000
   ```

## 🚀 Despliegue en Producción

### Usar HTTPS

1. Configurar certificado SSL
2. Actualizar URL en cámara a `https://`
3. Configurar nginx/apache como reverse proxy

### Usar IP Estática o Dominio

En la cámara, configurar:

```
URL: https://api.tudominio.com/detections/hikvision/event
```

### Monitoreo

Agregar endpoint de health check específico para cámaras:

```python
@router.get("/cameras/health")
async def cameras_health_check(db: AsyncSession = Depends(get_async_session)):
    """
    Verificar estado de todas las cámaras
    """
    cameras = await CameraService.get_all_cameras(db)

    results = []
    for camera in cameras:
        try:
            # Intentar capturar snapshot
            await capture_hikvision_snapshot(
                camera.ip_address,
                camera.username,
                camera.password
            )
            status = "online"
        except:
            status = "offline"

        results.append({
            "mac": camera.mac,
            "name": camera.name,
            "status": status
        })

    return results
```

## 📚 Referencias

- [Hikvision HTTP API](https://www.hikvision.com/en/support/download/sdk/)
- [ISAPI Documentation](https://www.hikvision.com/en/support/download/sdk/)
- [Event Notification Guide](https://www.hikvision.com/)
