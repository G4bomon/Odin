# 🤖 Integración de IA - Guía Completa

## 📋 Resumen

Este documento explica cómo integrar modelos de IA (YOLO, TensorFlow, PyTorch, etc.) para procesar automáticamente las detecciones de las cámaras.

## 🏗️ Arquitectura

```
┌─────────────────┐
│ Cámara/Móvil    │
└────────┬────────┘
         │ POST /detections/upload
         ▼
┌─────────────────────────────────┐
│ FastAPI Backend                 │
│ - Guarda imagen                 │
│ - Crea detección (processed=False)│
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Worker de IA (Background)       │
│ - Busca detecciones pendientes  │
│ - Procesa con modelo de IA      │
│ - Actualiza resultados          │
└─────────────────────────────────┘
```

## 📁 Archivos Creados

### 1. **`app/ai/processor.py`** - Procesador de IA

Clase principal que carga y ejecuta el modelo de IA.

**Métodos principales:**

- `load_model()` - Carga el modelo en memoria
- `process_image(image_path)` - Procesa una imagen
- `process_batch(image_paths)` - Procesa múltiples imágenes

### 2. **`app/ai/worker.py`** - Worker en Background

Worker que busca detecciones pendientes y las procesa automáticamente.

**Características:**

- ✅ Ejecuta en background cada X segundos
- ✅ Busca detecciones con `processed=False`
- ✅ Procesa con el modelo de IA
- ✅ Actualiza la BD con resultados

### 3. **`app/ai/config.py`** - Configuración

Variables de configuración para el módulo de IA.

### 4. **`app/main.py`** - Actualizado

Ahora inicia/detiene el worker automáticamente al arrancar/apagar el servidor.

## 🚀 Cómo Integrar Tu Modelo de IA

### Opción 1: YOLO (Recomendado)

#### 1. Instalar dependencias:

```bash
pip install ultralytics opencv-python
```

#### 2. Editar `app/ai/processor.py`:

```python
from ultralytics import YOLO

class AIProcessor:
    async def load_model(self):
        if self.is_loaded:
            return

        # Cargar modelo YOLO
        self.model = YOLO(self.model_path or "yolov8n.pt")
        self.is_loaded = True
        logger.info(f"Modelo YOLO cargado: {self.model_path}")

    async def process_image(self, image_path: str) -> Dict[str, Any]:
        start_time = datetime.now()

        try:
            if not self.is_loaded:
                await self.load_model()

            # Ejecutar detección
            results = self.model(image_path)
            detections = results[0].boxes

            # Extraer objetos detectados
            objects_detected = []
            max_confidence = 0.0

            for box in detections:
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                class_name = self.model.names[cls]

                objects_detected.append({
                    "class": class_name,
                    "confidence": conf,
                    "bbox": box.xyxy[0].tolist()
                })

                if conf > max_confidence:
                    max_confidence = conf

            processing_time = (datetime.now() - start_time).total_seconds()

            return {
                "success": True,
                "objects_detected": objects_detected,
                "confidence": max_confidence,
                "detection_type": objects_detected[0]["class"] if objects_detected else "none",
                "processing_time": processing_time,
                "error_message": None
            }

        except Exception as e:
            # ... manejo de errores
```

### Opción 2: TensorFlow

```python
import tensorflow as tf
import numpy as np
from PIL import Image

class AIProcessor:
    async def load_model(self):
        self.model = tf.saved_model.load(self.model_path)
        self.is_loaded = True

    async def process_image(self, image_path: str):
        # Cargar y preprocesar imagen
        img = Image.open(image_path)
        img_array = np.array(img)

        # Ejecutar inferencia
        predictions = self.model(img_array)

        # Procesar resultados...
```

### Opción 3: PyTorch

```python
import torch
from torchvision import transforms

class AIProcessor:
    async def load_model(self):
        self.model = torch.load(self.model_path)
        self.model.eval()
        self.is_loaded = True

    async def process_image(self, image_path: str):
        # Cargar y preprocesar
        transform = transforms.Compose([...])
        img = Image.open(image_path)
        img_tensor = transform(img)

        # Inferencia
        with torch.no_grad():
            predictions = self.model(img_tensor)
```

## ⚙️ Configuración

### Variables de Entorno (`.env`):

```env
# IA Configuration
AI_MODEL_PATH=models/yolov8n.pt
AI_WORKER_INTERVAL=5
AI_WORKER_ENABLED=true
AI_MIN_CONFIDENCE=0.5
AI_USE_GPU=true
AI_IMAGE_SIZE=640
```

### Descripción:

| Variable             | Descripción                    | Default             |
| -------------------- | ------------------------------ | ------------------- |
| `AI_MODEL_PATH`      | Ruta al modelo entrenado       | `models/yolov8n.pt` |
| `AI_WORKER_INTERVAL` | Segundos entre cada chequeo    | `5`                 |
| `AI_WORKER_ENABLED`  | Habilitar worker automático    | `true`              |
| `AI_MIN_CONFIDENCE`  | Confianza mínima               | `0.5`               |
| `AI_USE_GPU`         | Usar GPU si está disponible    | `true`              |
| `AI_IMAGE_SIZE`      | Tamaño de imagen para procesar | `640`               |

## 🎯 Flujo de Trabajo

### 1. Cámara envía imagen:

```bash
curl -X POST "http://localhost:8000/detections/upload" \
  -F "location_id=location_001" \
  -F "mac=AA:BB:CC:DD:EE:01" \
  -F "image_path=/path/to/image.jpg" \
  -F "image=@image.jpg"
```

### 2. Backend guarda en BD:

```python
Detection(
    location_id=1,
    camera_id=1,
    image_path="uploads/detections/uuid.jpg",
    processed=False  # ← Pendiente de procesar
)
```

### 3. Worker detecta y procesa:

```python
# Cada 5 segundos:
- Busca detecciones con processed=False
- Procesa con modelo de IA
- Actualiza:
  - processed=True
  - confidence=0.95
  - detection_type="person"
  - objects_detected=[...]
  - processing_time=0.123
```

### 4. Consultar resultados:

```bash
GET /detections/{id}
```

Respuesta:

```json
{
  "id": 1,
  "processed": true,
  "confidence": 0.95,
  "detection_type": "person",
  "objects_detected": [
    {
      "class": "person",
      "confidence": 0.95,
      "bbox": [100, 100, 200, 300]
    }
  ],
  "processing_time": 0.123,
  "created_at": "2024-01-01T10:00:00",
  "processed_at": "2024-01-01T10:00:05"
}
```

## 🔧 Uso Avanzado

### Procesar Manualmente (Sin Worker)

Si quieres procesar manualmente sin el worker automático:

```python
from app.ai.processor import get_ai_processor
from app.database import async_session_maker
from app.detections.models import Detection

async def process_detection_manually(detection_id: int):
    processor = get_ai_processor("models/yolov8n.pt")

    async with async_session_maker() as db:
        detection = await db.get(Detection, detection_id)
        result = await processor.process_image(detection.image_path)

        detection.processed = True
        detection.confidence = result["confidence"]
        detection.objects_detected = result["objects_detected"]

        await db.commit()
```

### Procesar en Batch

```python
from app.ai.processor import get_ai_processor

processor = get_ai_processor()
image_paths = ["img1.jpg", "img2.jpg", "img3.jpg"]
results = await processor.process_batch(image_paths)
```

### Deshabilitar Worker Automático

En `.env`:

```env
AI_WORKER_ENABLED=false
```

O crear un endpoint manual:

```python
@router.post("/detections/{id}/process")
async def process_detection(
    id: int,
    db: AsyncSession = Depends(get_async_session)
):
    processor = get_ai_processor()
    detection = await DetectionService.get_detection(db, id)
    result = await processor.process_image(detection.image_path)
    # Actualizar detección...
```

## 📊 Monitoreo

### Ver Estado del Worker

Agregar endpoint en `app/ai/routes.py`:

```python
from fastapi import APIRouter
from app.ai.worker import get_worker

router = APIRouter(prefix="/ai", tags=["ai"])

@router.get("/status")
async def get_ai_status():
    worker = get_worker()
    return {
        "is_running": worker.is_running,
        "interval_seconds": worker.interval_seconds,
        "model_path": worker.model_path
    }
```

## 🐛 Troubleshooting

### Worker no procesa detecciones

1. Verificar que `AI_WORKER_ENABLED=true` en `.env`
2. Verificar logs al iniciar el servidor:
   ```
   🤖 Iniciando worker de IA (intervalo: 5s)
   ```
3. Verificar que hay detecciones con `processed=False`

### Error al cargar modelo

1. Verificar que la ruta del modelo es correcta
2. Verificar que las dependencias están instaladas (`ultralytics`, etc.)
3. Verificar permisos de lectura del archivo del modelo

### Procesamiento muy lento

1. Reducir `AI_IMAGE_SIZE` en `.env`
2. Usar un modelo más pequeño (ej: `yolov8n.pt` en vez de `yolov8x.pt`)
3. Habilitar GPU: `AI_USE_GPU=true`
4. Aumentar `AI_WORKER_INTERVAL` para procesar menos frecuentemente

## 🎓 Próximos Pasos

1. **Entrenar tu propio modelo** con tus datos específicos
2. **Agregar filtros** por tipo de objeto detectado
3. **Implementar alertas** cuando se detecten objetos específicos
4. **Agregar dashboard** para visualizar estadísticas
5. **Implementar cache** para modelos grandes

## 📚 Recursos

- [Ultralytics YOLO](https://docs.ultralytics.com/)
- [TensorFlow](https://www.tensorflow.org/)
- [PyTorch](https://pytorch.org/)
- [OpenCV](https://opencv.org/)
