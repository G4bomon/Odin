# 🏗️ Arquitectura del Sistema Odin

## 📊 Diagrama General

```
┌─────────────────────────────────────────────────────────────────┐
│                        SISTEMA ODIN                              │
│                  Detección Inteligente con IA                    │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐         ┌──────────────────┐
│  Cámara Hikvision│         │  Móvil (Testing) │
│  - Motion Detect │         │  - HTML Test App │
│  - Line Crossing │         │  - Manual Upload │
└────────┬─────────┘         └────────┬─────────┘
         │                            │
         │ POST /detections/upload    │
         │ (multipart/form-data)      │
         └────────────┬───────────────┘
                      │
                      ▼
         ┌────────────────────────────┐
         │    FastAPI Backend         │
         │  ┌──────────────────────┐  │
         │  │  Authentication      │  │
         │  │  - JWT Tokens        │  │
         │  │  - Role-Based Access │  │
         │  └──────────────────────┘  │
         │  ┌──────────────────────┐  │
         │  │  Detections Module   │  │
         │  │  - Save Image        │  │
         │  │  - Create Record     │  │
         │  │  - processed=False   │  │
         │  └──────────────────────┘  │
         └────────────┬───────────────┘
                      │
                      ▼
         ┌────────────────────────────┐
         │   PostgreSQL Database      │
         │  ┌──────────────────────┐  │
         │  │ users                │  │
         │  │ locations            │  │
         │  │ cameras              │  │
         │  │ detections ←─────────┤  │
         │  │   - processed: bool  │  │
         │  │   - image_path       │  │
         │  └──────────────────────┘  │
         └────────────┬───────────────┘
                      │
                      │ Query: processed=False
                      │
                      ▼
         ┌────────────────────────────┐
         │   AI Worker (Background)   │
         │  ┌──────────────────────┐  │
         │  │  Every 5 seconds:    │  │
         │  │  1. Find pending     │  │
         │  │  2. Load image       │  │
         │  │  3. Run AI model     │  │
         │  │  4. Update DB        │  │
         │  └──────────────────────┘  │
         │  ┌──────────────────────┐  │
         │  │  AI Processor        │  │
         │  │  - YOLO / TensorFlow │  │
         │  │  - PyTorch / OpenCV  │  │
         │  └──────────────────────┘  │
         └────────────┬───────────────┘
                      │
                      │ Update results
                      │
                      ▼
         ┌────────────────────────────┐
         │   Detection Updated        │
         │  - processed: True         │
         │  - confidence: 0.95        │
         │  - detection_type: person  │
         │  - objects_detected: [...]  │
         │  - processing_time: 0.123s │
         └────────────────────────────┘
```

## 📁 Estructura de Archivos

```
Odin/
├── app/
│   ├── ai/                          # 🤖 Módulo de IA (NUEVO)
│   │   ├── __init__.py
│   │   ├── processor.py             # Procesador de IA
│   │   ├── worker.py                # Worker en background
│   │   └── config.py                # Configuración de IA
│   │
│   ├── api/
│   │   └── __init__.py              # Router principal
│   │
│   ├── cameras/
│   │   ├── models.py                # Modelo Camera
│   │   ├── schemas.py               # Schemas Pydantic
│   │   ├── routes.py                # Endpoints de cámaras
│   │   └── services.py              # Lógica de negocio
│   │
│   ├── core/
│   │   ├── roles.py                 # Sistema de roles
│   │   └── security.py              # Autenticación JWT
│   │
│   ├── detections/
│   │   ├── models.py                # Modelo Detection
│   │   ├── schemas.py               # Schemas Pydantic
│   │   ├── routes.py                # Endpoints de detecciones
│   │   └── services.py              # Lógica de negocio
│   │
│   ├── locations/
│   │   ├── models.py                # Modelo Location
│   │   ├── schemas.py               # Schemas Pydantic
│   │   ├── routes.py                # Endpoints de ubicaciones
│   │   └── services.py              # Lógica de negocio
│   │
│   ├── users/
│   │   ├── models.py                # Modelo User
│   │   ├── schemas.py               # Schemas Pydantic
│   │   ├── routes.py                # Endpoints de usuarios
│   │   └── services.py              # UserManager
│   │
│   ├── config.py                    # Configuración general
│   ├── database.py                  # SQLAlchemy setup
│   └── main.py                      # FastAPI app + Worker startup
│
├── alembic/                         # Migraciones de BD
│   ├── versions/
│   └── env.py
│
├── uploads/                         # Imágenes subidas
│   └── detections/
│
├── models/                          # Modelos de IA (NUEVO)
│   └── yolov8n.pt
│
├── seeds.py                         # Seeder de datos
├── reset_db.py                      # Reset de BD
├── AI_INTEGRATION.md                # Guía de integración IA
├── HIKVISION_INTEGRATION.md         # Guía Hikvision
├── SEEDING.md                       # Guía de seeding
└── requirements.txt
```

## 🔄 Flujo de Datos Completo

### 1. **Registro de Cámara**

```
Admin → POST /cameras → DB
- Registrar MAC, IP, ubicación
- Guardar credenciales
```

### 2. **Detección de Evento**

```
Cámara → Detecta movimiento → Envía a Backend
- POST /detections/upload
- Incluye: location_id, mac, imagen
```

### 3. **Almacenamiento**

```
Backend → Valida → Guarda
- Verificar cámara existe
- Verificar ubicación existe
- Guardar imagen en disco
- Crear registro en DB (processed=False)
```

### 4. **Procesamiento IA (Automático)**

```
Worker → Cada 5s → Busca pendientes
- Query: SELECT * WHERE processed=False
- Para cada detección:
  - Cargar imagen
  - Ejecutar modelo IA
  - Extraer objetos detectados
  - Actualizar DB (processed=True)
```

### 5. **Consulta de Resultados**

```
Usuario → GET /detections/{id} → Resultados
- Ver imagen procesada
- Ver objetos detectados
- Ver confianza y tipo
```

## 🎯 Archivos Clave para Modificar

### Para Integrar Tu Modelo de IA:

**`app/ai/processor.py`** - Líneas 40-60

```python
async def load_model(self):
    # AQUÍ: Cargar tu modelo
    # Ejemplo: self.model = YOLO("yolov8n.pt")
    pass

async def process_image(self, image_path: str):
    # AQUÍ: Procesar imagen con tu modelo
    # Ejemplo: results = self.model(image_path)
    pass
```

### Para Configurar Parámetros:

**`.env`**

```env
AI_MODEL_PATH=models/yolov8n.pt
AI_WORKER_INTERVAL=5
AI_WORKER_ENABLED=true
```

### Para Agregar Endpoints Personalizados:

**`app/detections/routes.py`**

```python
@router.post("/custom-endpoint")
async def custom_detection_endpoint(...):
    # Tu lógica aquí
    pass
```

## 🔐 Sistema de Roles

```
SUPERADMIN (Nivel 4)
    ├── Acceso total
    └── Gestión de usuarios y roles

ADMIN (Nivel 3)
    ├── Gestión de empresas
    ├── Gestión de ubicaciones
    └── Gestión de cámaras

EMPRESA (Nivel 2)
    ├── Ver sus ubicaciones
    ├── Ver sus cámaras
    └── Ver detecciones

USUARIO (Nivel 1)
    └── Ver detecciones asignadas
```

## 📊 Modelos de Base de Datos

### User

```python
- id: int (PK)
- email: str (unique)
- hashed_password: str
- role: RoleEnum
- is_active: bool
- is_superuser: bool
```

### Location

```python
- id: int (PK)
- location_id: str (unique, ej: "location_001")
- name: str
- address: str
- is_active: bool
```

### Camera

```python
- id: int (PK)
- mac: str (unique)
- name: str
- model: str
- location_id: int (FK → locations)
- ip_address: str
- username: str
- password: str
```

### Detection

```python
- id: int (PK)
- location_id: int (FK → locations)
- camera_id: int (FK → cameras)
- image_path: str
- processed: bool
- confidence: float
- detection_type: str
- objects_detected: JSON
- processing_time: float
- error_message: str
- created_at: datetime
- processed_at: datetime
```

## 🚀 Endpoints Principales

### Autenticación

- `POST /auth/jwt/login` - Login
- `POST /auth/jwt/logout` - Logout
- `POST /auth/register` - Registro

### Ubicaciones

- `GET /locations` - Listar ubicaciones
- `POST /locations` - Crear ubicación
- `GET /locations/{id}` - Ver ubicación
- `PUT /locations/{id}` - Actualizar ubicación
- `DELETE /locations/{id}` - Eliminar ubicación

### Cámaras

- `GET /cameras` - Listar cámaras
- `POST /cameras` - Crear cámara
- `GET /cameras/{id}` - Ver cámara
- `PUT /cameras/{id}` - Actualizar cámara
- `DELETE /cameras/{id}` - Eliminar cámara

### Detecciones

- `POST /detections/upload` - Subir detección (cámara/móvil)
- `GET /detections` - Listar detecciones
- `GET /detections/{id}` - Ver detección
- `GET /detections/{id}/details` - Ver detalles completos
- `GET /detections/stats` - Estadísticas

## 🔧 Tecnologías Utilizadas

- **Backend**: FastAPI 0.121.3
- **Base de Datos**: PostgreSQL 15 + asyncpg
- **ORM**: SQLAlchemy 2.0 (async)
- **Autenticación**: FastAPI Users + JWT
- **Migraciones**: Alembic
- **IA**: Ultralytics YOLO / TensorFlow / PyTorch
- **Password Hashing**: Bcrypt
- **Validación**: Pydantic

## 📈 Escalabilidad

### Para Producción:

1. **Separar Worker de API**

   - Ejecutar worker en servidor separado
   - Usar Redis/RabbitMQ para cola de tareas

2. **Load Balancer**

   - Nginx/Apache como reverse proxy
   - Múltiples instancias de FastAPI

3. **Cache**

   - Redis para resultados frecuentes
   - Cache de modelos en memoria

4. **Almacenamiento**

   - S3/MinIO para imágenes
   - CDN para servir imágenes

5. **Monitoreo**
   - Prometheus + Grafana
   - Sentry para errores
   - ELK Stack para logs

## 🎓 Próximos Pasos

1. ✅ Integrar tu modelo de IA en `app/ai/processor.py`
2. ✅ Configurar cámaras Hikvision reales
3. ✅ Entrenar modelo con tus datos específicos
4. ✅ Agregar dashboard de visualización
5. ✅ Implementar sistema de alertas
6. ✅ Agregar API de reportes
7. ✅ Implementar cache y optimizaciones
