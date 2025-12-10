# 🌱 Database Seeding - Guía de Uso

## 📋 Descripción

Este proyecto incluye scripts para poblar la base de datos con datos iniciales de prueba y desarrollo.

## 🚀 Uso Rápido

### 1. Ejecutar Migraciones

Primero, asegúrate de que la base de datos esté actualizada:

```bash
alembic upgrade head
```

### 2. Poblar la Base de Datos

```bash
python seeds.py
```

### 3. (Opcional) Resetear la Base de Datos

Si necesitas empezar de cero:

```bash
python reset_db.py
```

⚠️ **ADVERTENCIA**: Esto eliminará TODOS los datos.

## 📊 Datos Creados por el Seeder

### 👤 Usuarios

El seeder crea 4 usuarios con diferentes roles:

| Email                 | Password     | Rol        | Descripción                      |
| --------------------- | ------------ | ---------- | -------------------------------- |
| `superadmin@odin.com` | `super123`   | SUPERADMIN | Acceso total al sistema          |
| `admin@odin.com`      | `admin123`   | ADMIN      | Gestión de empresas y usuarios   |
| `empresa@odin.com`    | `empresa123` | EMPRESA    | Gestión de ubicaciones y cámaras |
| `dev@odin.com`        | `dev123`     | EMPRESA    | Usuario para desarrollo          |

### 📍 Locations (Ubicaciones)

| location_id    | Nombre             | Descripción               |
| -------------- | ------------------ | ------------------------- |
| `location_001` | Patio Principal    | Área de entrada principal |
| `location_002` | Almacén General    | Zona de almacenamiento    |
| `location_003` | Oficinas Centrales | Área administrativa       |
| `location_004` | Estacionamiento    | Zona de estacionamiento   |
| `mi_casa`      | Mi Casa            | Ubicación de prueba       |

### 📷 Cameras (Cámaras)

| MAC Address         | Nombre                   | Modelo                   | Location           |
| ------------------- | ------------------------ | ------------------------ | ------------------ |
| `AA:BB:CC:DD:EE:01` | Cámara Entrada Principal | Hikvision DS-2CD2143G0-I | Patio Principal    |
| `AA:BB:CC:DD:EE:02` | Cámara Almacén 1         | Hikvision DS-2CD2143G0-I | Almacén General    |
| `AA:BB:CC:DD:EE:03` | Cámara Oficinas          | Hikvision DS-2CD2143G0-I | Oficinas Centrales |
| `AA:BB:CC:DD:EE:04` | Cámara Estacionamiento   | Hikvision DS-2CD2143G0-I | Estacionamiento    |
| `AA:BB:CC:DD:EE:05` | Teléfono Móvil           | Smartphone               | Mi Casa            |

## 🔧 Personalización

### Agregar Más Datos

Edita `seeds.py` y agrega tus datos en las secciones correspondientes:

```python
# Ejemplo: Agregar una nueva ubicación
{
    "location_id": "location_005",
    "name": "Nueva Ubicación",
    "description": "Descripción de la ubicación",
    "address": "Dirección física",
    "is_active": True
}
```

### Modificar Contraseñas

Las contraseñas se hashean automáticamente usando bcrypt. Para cambiarlas, edita:

```python
"hashed_password": get_password_hash("tu_nueva_password")
```

## 🔄 Workflow Recomendado

### Desarrollo Local

1. **Primera vez:**

   ```bash
   alembic upgrade head
   python seeds.py
   ```

2. **Después de cambios en modelos:**

   ```bash
   alembic revision --autogenerate -m "descripción del cambio"
   alembic upgrade head
   ```

3. **Si necesitas datos frescos:**
   ```bash
   python reset_db.py
   alembic upgrade head
   python seeds.py
   ```

### Testing

Para pruebas, puedes ejecutar el seeder múltiples veces. Los datos duplicados no se crearán gracias a la función `create_if_not_exists()`.

## 📝 Notas Importantes

- ✅ El seeder es **idempotente**: Puedes ejecutarlo múltiples veces sin crear duplicados
- ✅ Usa **async/await** para compatibilidad con SQLAlchemy async
- ✅ Las contraseñas se **hashean automáticamente** con bcrypt
- ⚠️ `reset_db.py` requiere confirmación manual para evitar borrados accidentales

## 🐛 Troubleshooting

### Error: "Table already exists"

Si ves este error, probablemente necesitas ejecutar las migraciones:

```bash
alembic upgrade head
```

### Error: "No module named 'app'"

Asegúrate de estar en el directorio raíz del proyecto:

```bash
cd c:\Users\isaac\Documents\GitHub\Odin
python seeds.py
```

### Error de conexión a PostgreSQL

Verifica que PostgreSQL esté corriendo y que el `.env` tenga la configuración correcta:

```env
DATABASE_URL=postgresql+asyncpg://usuario:password@localhost:5432/odin_db
```

## 🎯 Próximos Pasos

Después de ejecutar el seeder, puedes:

1. **Probar la API**: Ve a `http://localhost:8000/docs`
2. **Login**: Usa cualquiera de las credenciales de arriba
3. **Probar endpoints**: Usa Postman o la interfaz Swagger
4. **Enviar detecciones**: Usa la app móvil de prueba en `http://localhost:8000/mobile`

## 📚 Referencias

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [FastAPI Users](https://fastapi-users.github.io/fastapi-users/)
