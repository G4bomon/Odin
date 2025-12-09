# 📸 Guía de API de Detecciones - Odin Vision

Documentación completa del sistema de detecciones para cámaras Hikvision.

## 📋 Tabla de Contenidos

- [Arquitectura](#arquitectura)
- [Modelos de Datos](#modelos-de-datos)
- [Endpoints](#endpoints)
- [Ejemplos de Uso](#ejemplos-de-uso)
- [Integración con Cámaras](#integración-con-cámaras)

---

## 🏗️ Arquitectura

El sistema está dividido en 3 dominios principales:

### 1. **Patios** (`/patios`)

Gestión de ubicaciones físicas donde se instalan las cámaras.

### 2. **Cámaras** (`/cameras`)

Gestión de cámaras Hikvision instaladas en los patios.

### 3. **Detecciones** (`/detections`)

Recepción y procesamiento de detecciones de IA desde las cámaras.

---

## 📊 Modelos de Datos

### Patio

```json
{
  "id": 1,
  "patio_id": "patio_001",
  "name": "Patio Principal",
  "description": "Patio de entrada principal",
  "location": "Edificio A, Planta Baja",
  "is_active": true,
  "created_at": "2025-12-09T10:00:00",
  "updated_at": "2025-12-09T10:00:00"
}
```

### Cámara

```json
{
  "id": 1,
  "mac": "AA:BB:CC:DD:EE:FF",
  "name": "Cámara Entrada",
  "model": "Hikvision DS-2CD2143G0-I",
  "ip_address": "192.168.1.100",
  "patio_id": 1,
  "is_active": true,
  "last_detection": "2025-12-09T10:30:00",
  "created_at": "2025-12-09T10:00:00",
  "updated_at": "2025-12-09T10:00:00"
}
```

### Detección

```json
{
  "id": 1,
  "patio_id": 1,
  "camera_id": 1,
  "image_path": "/path/to/image.jpg",
  "image_url": "https://storage.example.com/image.jpg",
  "detection_type": "threat",
  "confidence": 0.95,
  "objects_detected": {
    "objects": [
      {
        "class": "person",
        "confidence": 0.98,
        "bbox": [100, 200, 300, 400]
      }
    ]
  },
  "processed": true,
  "processing_time": 0.5,
  "error_message": null,
  "created_at": "2025-12-09T10:30:00",
  "processed_at": "2025-12-09T10:30:01"
}
```

---

## 🔌 Endpoints

### Patios

#### `POST /patios` - Crear patio

**Requiere:** ADMIN+

```bash
curl -X POST "http://localhost:8000/patios" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patio_id": "patio_001",
    "name": "Patio Principal",
    "description": "Patio de entrada principal",
    "location": "Edificio A, Planta Baja",
    "is_active": true
  }'
```

#### `GET /patios` - Listar patios

**Requiere:** EMPRESA+

```bash
curl -X GET "http://localhost:8000/patios?skip=0&limit=100&is_active=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### `GET /patios/{patio_id}` - Obtener patio

**Requiere:** EMPRESA+

```bash
curl -X GET "http://localhost:8000/patios/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### `GET /patios/{patio_id}/stats` - Estadísticas del patio

**Requiere:** EMPRESA+

```bash
curl -X GET "http://localhost:8000/patios/1/stats" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Respuesta:**

```json
{
  "id": 1,
  "patio_id": "patio_001",
  "name": "Patio Principal",
  "total_cameras": 5,
  "active_cameras": 4,
  "total_detections": 150
}
```

#### `PATCH /patios/{patio_id}` - Actualizar patio

**Requiere:** ADMIN+

```bash
curl -X PATCH "http://localhost:8000/patios/1" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Patio Principal Actualizado",
    "is_active": false
  }'
```

#### `DELETE /patios/{patio_id}` - Eliminar patio

**Requiere:** ADMIN+

```bash
curl -X DELETE "http://localhost:8000/patios/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### Cámaras

#### `POST /cameras` - Crear cámara

**Requiere:** ADMIN+

```bash
curl -X POST "http://localhost:8000/cameras" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "mac": "AA:BB:CC:DD:EE:FF",
    "name": "Cámara Entrada",
    "model": "Hikvision DS-2CD2143G0-I",
    "ip_address": "192.168.1.100",
    "patio_id": 1,
    "is_active": true
  }'
```

#### `GET /cameras` - Listar cámaras

**Requiere:** EMPRESA+

```bash
curl -X GET "http://localhost:8000/cameras?patio_id=1&is_active=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### `GET /cameras/{camera_id}` - Obtener cámara

**Requiere:** EMPRESA+

```bash
curl -X GET "http://localhost:8000/cameras/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### `GET /cameras/mac/{mac}` - Obtener cámara por MAC

**Requiere:** EMPRESA+

```bash
curl -X GET "http://localhost:8000/cameras/mac/AA:BB:CC:DD:EE:FF" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### `GET /cameras/{camera_id}/stats` - Estadísticas de cámara

**Requiere:** EMPRESA+

```bash
curl -X GET "http://localhost:8000/cameras/1/stats" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Respuesta:**

```json
{
  "id": 1,
  "mac": "AA:BB:CC:DD:EE:FF",
  "name": "Cámara Entrada",
  "total_detections": 50,
  "detections_today": 10
}
```

---

### Detecciones

#### `POST /detections/upload` - **Endpoint principal para cámaras**

**NO requiere autenticación** (para que las cámaras puedan enviar datos)

Este es el endpoint que usarán las cámaras Hikvision para enviar detecciones.

**Formato:** `multipart/form-data`

```bash
curl -X POST "http://localhost:8000/detections/upload" \
  -F "patio_id=patio_001" \
  -F "mac=AA:BB:CC:DD:EE:FF" \
  -F "image_path=/path/to/image.jpg" \
  -F "image=@image.jpg"
```

**Respuesta exitosa:**

```json
{
  "success": true,
  "message": "Detección recibida correctamente",
  "detection_id": 123
}
```

**Respuesta con error:**

```json
{
  "success": false,
  "message": "Error al procesar la detección",
  "error": "Cámara con MAC AA:BB:CC:DD:EE:FF no encontrada"
}
```

#### `POST /detections` - Crear detección manual

**Requiere:** EMPRESA+

```bash
curl -X POST "http://localhost:8000/detections" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patio_id": 1,
    "camera_id": 1,
    "image_path": "/path/to/image.jpg",
    "detection_type": "threat",
    "confidence": 0.95
  }'
```

#### `GET /detections` - Listar detecciones

**Requiere:** EMPRESA+

```bash
curl -X GET "http://localhost:8000/detections?patio_id=1&processed=false&limit=50" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Filtros disponibles:**

- `skip`: Offset para paginación (default: 0)
- `limit`: Límite de resultados (default: 100)
- `patio_id`: Filtrar por patio
- `camera_id`: Filtrar por cámara
- `processed`: Filtrar por estado de procesamiento (true/false)
- `detection_type`: Filtrar por tipo de detección

#### `GET /detections/stats` - Estadísticas generales

**Requiere:** EMPRESA+

```bash
curl -X GET "http://localhost:8000/detections/stats" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Respuesta:**

```json
{
  "total_detections": 1000,
  "processed_detections": 950,
  "pending_detections": 50,
  "detections_today": 100,
  "detections_this_week": 500,
  "detections_this_month": 1000,
  "average_confidence": 0.92,
  "average_processing_time": 0.45
}
```

#### `GET /detections/{detection_id}` - Obtener detección

**Requiere:** EMPRESA+

```bash
curl -X GET "http://localhost:8000/detections/123" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### `GET /detections/{detection_id}/details` - Detección con detalles

**Requiere:** EMPRESA+

```bash
curl -X GET "http://localhost:8000/detections/123/details" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Respuesta:**

```json
{
  "id": 123,
  "patio_id": 1,
  "camera_id": 1,
  "patio_name": "Patio Principal",
  "camera_name": "Cámara Entrada",
  "camera_mac": "AA:BB:CC:DD:EE:FF",
  "image_path": "/path/to/image.jpg",
  "detection_type": "threat",
  "confidence": 0.95,
  "processed": true
}
```

#### `PATCH /detections/{detection_id}` - Actualizar detección

**Requiere:** EMPRESA+

Útil para actualizar resultados del procesamiento de IA.

```bash
curl -X PATCH "http://localhost:8000/detections/123" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "detection_type": "threat",
    "confidence": 0.95,
    "objects_detected": {
      "objects": [
        {
          "class": "person",
          "confidence": 0.98,
          "bbox": [100, 200, 300, 400]
        }
      ]
    },
    "processed": true,
    "processing_time": 0.5
  }'
```

---

## 🎯 Ejemplos de Uso Completo

### Flujo 1: Configuración Inicial

```bash
# 1. Crear un patio
curl -X POST "http://localhost:8000/patios" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patio_id": "patio_001",
    "name": "Patio Principal",
    "location": "Edificio A"
  }'

# 2. Crear una cámara en ese patio
curl -X POST "http://localhost:8000/cameras" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "mac": "AA:BB:CC:DD:EE:FF",
    "name": "Cámara Entrada",
    "ip_address": "192.168.1.100",
    "patio_id": 1
  }'
```

### Flujo 2: Recepción de Detección desde Cámara

```bash
# La cámara envía una detección (sin autenticación)
curl -X POST "http://localhost:8000/detections/upload" \
  -F "patio_id=patio_001" \
  -F "mac=AA:BB:CC:DD:EE:FF" \
  -F "image_path=/captures/2025-12-09/image_001.jpg" \
  -F "image=@image_001.jpg"
```

### Flujo 3: Procesamiento de IA

```bash
# 1. Obtener detecciones pendientes
curl -X GET "http://localhost:8000/detections?processed=false&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 2. Procesar con IA (tu modelo)
# ... procesamiento ...

# 3. Actualizar con resultados
curl -X PATCH "http://localhost:8000/detections/123" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "detection_type": "threat",
    "confidence": 0.95,
    "objects_detected": {
      "threat_level": "high",
      "objects": ["weapon", "person"]
    },
    "processed": true,
    "processing_time": 0.5
  }'
```

### Flujo 4: Monitoreo y Estadísticas

```bash
# Ver estadísticas generales
curl -X GET "http://localhost:8000/detections/stats" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Ver estadísticas de un patio
curl -X GET "http://localhost:8000/patios/1/stats" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Ver estadísticas de una cámara
curl -X GET "http://localhost:8000/cameras/1/stats" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🎥 Integración con Cámaras Hikvision

### Configuración en la Cámara

En el sistema de la cámara Hikvision, configura:

1. **API URL:** `http://your-server.com/detections/upload`
2. **Método:** `POST`
3. **Content-Type:** `multipart/form-data`
4. **Timeout:** 5 segundos

### Parámetros que debe enviar la cámara:

| Campo        | Tipo   | Descripción                  | Ejemplo               |
| ------------ | ------ | ---------------------------- | --------------------- |
| `patio_id`   | string | ID del patio configurado     | `patio_001`           |
| `mac`        | string | MAC address de la cámara     | `AA:BB:CC:DD:EE:FF`   |
| `image_path` | string | Ruta de la imagen            | `/captures/image.jpg` |
| `image`      | file   | Archivo de imagen (opcional) | `image.jpg`           |

### Ejemplo de código Python para simular cámara:

```python
import requests

def send_detection(patio_id: str, mac: str, image_path: str, image_file: str):
    url = "http://localhost:8000/detections/upload"

    data = {
        'patio_id': patio_id,
        'mac': mac,
        'image_path': image_path
    }

    files = {
        'image': open(image_file, 'rb')
    }

    response = requests.post(url, data=data, files=files, timeout=5)
    return response.json()

# Uso
result = send_detection(
    patio_id="patio_001",
    mac="AA:BB:CC:DD:EE:FF",
    image_path="/captures/image.jpg",
    image_file="./image.jpg"
)

print(result)
# {'success': True, 'message': 'Detección recibida correctamente', 'detection_id': 123}
```

---

## 🔐 Permisos por Rol

| Endpoint                | SUPERADMIN | ADMIN | EMPRESA | USUARIO |
| ----------------------- | ---------- | ----- | ------- | ------- |
| POST /patios            | ✅         | ✅    | ❌      | ❌      |
| GET /patios             | ✅         | ✅    | ✅      | ❌      |
| PATCH /patios           | ✅         | ✅    | ❌      | ❌      |
| DELETE /patios          | ✅         | ✅    | ❌      | ❌      |
| POST /cameras           | ✅         | ✅    | ❌      | ❌      |
| GET /cameras            | ✅         | ✅    | ✅      | ❌      |
| PATCH /cameras          | ✅         | ✅    | ❌      | ❌      |
| DELETE /cameras         | ✅         | ✅    | ❌      | ❌      |
| POST /detections/upload | 🌐         | 🌐    | 🌐      | 🌐      |
| GET /detections         | ✅         | ✅    | ✅      | ❌      |
| PATCH /detections       | ✅         | ✅    | ✅      | ❌      |

🌐 = Sin autenticación (público)

---

## 📝 Notas Importantes

1. **El endpoint `/detections/upload` NO requiere autenticación** para permitir que las cámaras envíen datos sin complicaciones.

2. **Validaciones automáticas:**

   - MAC address debe tener formato válido (AA:BB:CC:DD:EE:FF)
   - IP address debe ser válida
   - La cámara debe existir y estar registrada
   - El patio debe existir
   - La cámara debe pertenecer al patio especificado

3. **Procesamiento asíncrono:** Las detecciones se crean con `processed=false` y deben ser procesadas por tu modelo de IA posteriormente.

4. **Almacenamiento de imágenes:** El campo `image_path` guarda la ruta original. Puedes implementar lógica para subir a cloud storage y guardar la URL en `image_url`.

---

## 🚀 Próximos Pasos

1. Ejecutar migraciones: `alembic upgrade head`
2. Crear patios y cámaras de prueba
3. Probar endpoint de upload con Postman
4. Integrar con tu modelo de IA
5. Implementar almacenamiento de imágenes en cloud

---

**Última actualización:** Diciembre 2025
