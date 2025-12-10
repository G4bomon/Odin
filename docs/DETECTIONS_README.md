# 📸 Sistema de Detecciones - Odin Vision

Sistema completo de gestión de detecciones para cámaras Hikvision con procesamiento de IA.

## 🎯 ¿Qué es esto?

Este backend gestiona la información que envían las cámaras Hikvision para el proyecto **Odin Vision**, un sistema de reconocimiento visual multipropósito que incluye:

- 🛡️ **Odin Sentinel** - Detección de amenazas y comportamientos anómalos
- 👤 **Odin Identity** - Reconocimiento facial biométrico
- 📦 **Odin Classify** - Clasificación de objetos

## 🏗️ Arquitectura

```
┌─────────────────┐
│ Cámara Hikvision│
│  (MAC: AA:BB:.) │
└────────┬────────┘
         │ POST /detections/upload
         │ (multipart/form-data)
         ▼
┌─────────────────────────┐
│   Backend FastAPI       │
│  ┌─────────────────┐   │
│  │ Patios          │   │
│  │ Cámaras         │   │
│  │ Detecciones     │   │
│  └─────────────────┘   │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│   PostgreSQL DB         │
│  - patios               │
│  - cameras              │
│  - detections           │
└─────────────────────────┘
         │
         ▼
┌─────────────────────────┐
│   Modelo de IA          │
│  (Procesamiento)        │
└─────────────────────────┘
```

## 📦 Dominios Implementados

### 1. **Patios** (`/patios`)

Gestión de ubicaciones físicas donde se instalan las cámaras.

**Campos principales:**

- `patio_id`: ID único (ej: "patio_001")
- `name`: Nombre del patio
- `location`: Ubicación física
- `is_active`: Estado activo/inactivo

### 2. **Cámaras** (`/cameras`)

Gestión de cámaras Hikvision.

**Campos principales:**

- `mac`: MAC address (ej: "AA:BB:CC:DD:EE:FF")
- `name`: Nombre de la cámara
- `model`: Modelo de la cámara
- `ip_address`: Dirección IP
- `patio_id`: Patio donde está instalada

### 3. **Detecciones** (`/detections`)

Recepción y procesamiento de detecciones de IA.

**Campos principales:**

- `patio_id`: ID del patio
- `camera_id`: ID de la cámara
- `image_path`: Ruta de la imagen
- `detection_type`: Tipo de detección (threat, face, object)
- `confidence`: Confianza de la detección (0-1)
- `objects_detected`: JSON con objetos detectados
- `processed`: Estado de procesamiento

## 🚀 Inicio Rápido

### 1. Ejecutar Migraciones

```bash
# Aplicar migraciones
alembic upgrade head
```

### 2. Crear Datos de Prueba

```bash
# Opción 1: Usar el script de prueba
python test_detections.py

# Opción 2: Usar Postman
# Importar: Odin_API.postman_collection.json
```

### 3. Configurar Patio y Cámara

```bash
# 1. Crear patio
curl -X POST "http://localhost:8000/patios" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patio_id": "patio_001",
    "name": "Patio Principal",
    "location": "Edificio A"
  }'

# 2. Crear cámara
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

### 4. Probar Recepción de Detección

```bash
# Simular envío desde cámara (SIN autenticación)
curl -X POST "http://localhost:8000/detections/upload" \
  -F "patio_id=patio_001" \
  -F "mac=AA:BB:CC:DD:EE:FF" \
  -F "image_path=/path/to/image.jpg" \
  -F "image=@image.jpg"
```

## 📡 Endpoint Principal para Cámaras

### `POST /detections/upload`

**Este es el endpoint que usarán las cámaras Hikvision.**

**Características:**

- ✅ NO requiere autenticación
- ✅ Acepta `multipart/form-data`
- ✅ Valida que la cámara y el patio existan
- ✅ Guarda la detección para procesamiento posterior

**Parámetros:**

| Campo        | Tipo   | Requerido | Descripción                    |
| ------------ | ------ | --------- | ------------------------------ |
| `patio_id`   | string | Sí        | ID del patio (ej: "patio_001") |
| `mac`        | string | Sí        | MAC address de la cámara       |
| `image_path` | string | Sí        | Ruta de la imagen              |
| `image`      | file   | No        | Archivo de imagen              |

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

## 🔄 Flujo de Procesamiento

```
1. Cámara detecta movimiento/evento
   ↓
2. Cámara envía imagen a /detections/upload
   ↓
3. Backend guarda detección (processed=false)
   ↓
4. Sistema obtiene detecciones pendientes
   GET /detections?processed=false
   ↓
5. Modelo de IA procesa la imagen
   ↓
6. Backend actualiza detección con resultados
   PATCH /detections/{id}
   {
     "detection_type": "threat",
     "confidence": 0.95,
     "objects_detected": {...},
     "processed": true
   }
   ↓
7. Dashboard muestra resultados
```

## 📊 Estadísticas Disponibles

### Estadísticas Generales

```bash
GET /detections/stats
```

Retorna:

- Total de detecciones
- Detecciones procesadas/pendientes
- Detecciones por período (hoy, semana, mes)
- Confianza promedio
- Tiempo de procesamiento promedio

### Estadísticas por Patio

```bash
GET /patios/{patio_id}/stats
```

Retorna:

- Total de cámaras
- Cámaras activas
- Total de detecciones

### Estadísticas por Cámara

```bash
GET /cameras/{camera_id}/stats
```

Retorna:

- Total de detecciones
- Detecciones de hoy

## 🔐 Permisos

| Acción                 | Rol Requerido         |
| ---------------------- | --------------------- |
| Crear/editar patios    | ADMIN+                |
| Crear/editar cámaras   | ADMIN+                |
| Ver patios/cámaras     | EMPRESA+              |
| Ver detecciones        | EMPRESA+              |
| Actualizar detecciones | EMPRESA+              |
| **Enviar detección**   | **Ninguno (público)** |

## 🗂️ Estructura de Archivos

```
app/
├── patios/
│   ├── models.py       # Modelo Patio
│   ├── schemas.py      # Schemas Pydantic
│   ├── services.py     # Lógica de negocio
│   └── routes.py       # Endpoints
├── cameras/
│   ├── models.py       # Modelo Camera
│   ├── schemas.py      # Schemas Pydantic
│   ├── services.py     # Lógica de negocio
│   └── routes.py       # Endpoints
└── detections/
    ├── models.py       # Modelo Detection
    ├── schemas.py      # Schemas Pydantic
    ├── services.py     # Lógica de negocio
    └── routes.py       # Endpoints
```

## 🧪 Pruebas

### Opción 1: Script Python

```bash
# 1. Configurar token en test_detections.py
# 2. Ejecutar
python test_detections.py
```

### Opción 2: Postman

1. Importar `Odin_API.postman_collection.json`
2. Configurar variable `{{token}}`
3. Ejecutar colección

### Opción 3: Swagger UI

```
http://localhost:8000/docs
```

## 📝 Ejemplo de Integración con IA

```python
import requests

# 1. Obtener detecciones pendientes
response = requests.get(
    "http://localhost:8000/detections?processed=false",
    headers={"Authorization": f"Bearer {token}"}
)
detections = response.json()

# 2. Procesar cada detección
for detection in detections:
    # Cargar imagen
    image = load_image(detection['image_path'])

    # Procesar con tu modelo de IA
    results = your_ai_model.predict(image)

    # Actualizar detección
    requests.patch(
        f"http://localhost:8000/detections/{detection['id']}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "detection_type": results['type'],
            "confidence": results['confidence'],
            "objects_detected": results['objects'],
            "processed": True,
            "processing_time": results['time']
        }
    )
```

## 🔧 Configuración de Cámara Hikvision

En el panel de administración de la cámara:

1. **Event Settings** → **Smart Event**
2. Configurar **HTTP Notification**:
   - URL: `http://your-server.com/detections/upload`
   - Method: `POST`
   - Content-Type: `multipart/form-data`
3. Agregar parámetros:
   - `patio_id`: ID del patio
   - `mac`: MAC de la cámara
   - `image_path`: Ruta de la imagen
4. Habilitar envío de imagen

## 📚 Documentación Adicional

- [DETECTIONS_API_GUIDE.md](./DETECTIONS_API_GUIDE.md) - Guía completa de API
- [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) - Estructura del proyecto
- [ROLES_GUIDE.md](./ROLES_GUIDE.md) - Sistema de roles

## 🌐 Landing Page

Visita el landing page del proyecto:
**https://odin-vision.vercel.app**

## 🤝 Contribuir

Ver [CONTRIBUTING.md](./CONTRIBUTING.md)

---

**Desarrollado para Odin Vision** 🦅
