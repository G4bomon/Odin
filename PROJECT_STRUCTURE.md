# 📁 Estructura del Proyecto Odin

Documentación detallada de la estructura y componentes del proyecto.

## Árbol de Directorios

```
Odin/
├── app/                          # Código principal de la aplicación
│   ├── __init__.py
│   ├── main.py                   # Punto de entrada de FastAPI
│   ├── config.py                 # Configuración de la aplicación
│   ├── database.py               # Configuración de base de datos
│   │
│   ├── api/                      # Rutas y endpoints
│   │   ├── __init__.py           # Router principal
│   │   └── routes/
│   │       ├── auth.py           # Endpoints de autenticación
│   │       └── users.py          # Endpoints de gestión de usuarios
│   │
│   ├── core/                     # Lógica central
│   │   ├── security.py           # Configuración JWT y autenticación
│   │   └── users.py              # Lógica de gestión de usuarios
│   │
│   ├── models/                   # Modelos de base de datos (SQLAlchemy)
│   │   └── user.py               # Modelo de usuario
│   │
│   └── schemas/                  # Esquemas Pydantic (validación)
│       └── user.py               # Esquemas de usuario
│
├── alembic/                      # Migraciones de base de datos
│   ├── versions/                 # Archivos de migración
│   ├── env.py                    # Configuración de Alembic
│   └── script.py.mako            # Template de migración
│
├── .env.example                  # Ejemplo de variables de entorno
├── .env                          # Variables de entorno (no versionado)
├── .gitignore                    # Archivos a ignorar en Git
├── .dockerignore                 # Archivos a ignorar en Docker
├── alembic.ini                   # Configuración de Alembic
├── docker-compose.yml            # Orquestación de contenedores
├── Dockerfile                    # Imagen Docker de la aplicación
├── requirements.txt              # Dependencias de Python
├── README.md                     # Documentación principal
├── QUICK_START.md                # Guía rápida de inicio
├── CONTRIBUTING.md               # Guía de contribuciones
└── PROJECT_STRUCTURE.md          # Este archivo
```

## 📄 Descripción de Archivos Principales

### `app/main.py`

Punto de entrada de la aplicación FastAPI. Configura:
- Instancia de FastAPI
- Middleware CORS
- Routers de la API
- Endpoints de salud

```python
from fastapi import FastAPI
from app.api import api_router

app = FastAPI(title="Mi API con FastAPI Users")
app.include_router(api_router)
```

### `app/config.py`

Gestión centralizada de configuración usando Pydantic Settings:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    
    class Config:
        env_file = ".env"
```

### `app/database.py`

Configuración de la conexión a PostgreSQL con SQLAlchemy asincrónico:

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

engine = create_async_engine(settings.DATABASE_URL, echo=True)
async_session_maker = sessionmaker(engine, class_=AsyncSession)
```

### `app/models/user.py`

Modelo de usuario que extiende `SQLAlchemyBaseUserTable`:

```python
class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(1024))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=True)
    last_name: Mapped[str] = mapped_column(String(50), nullable=True)
```

**Campos:**
- `id`: Identificador único (entero)
- `email`: Correo electrónico único
- `hashed_password`: Contraseña hasheada con Argon2
- `is_active`: Usuario activo/inactivo
- `is_superuser`: Permisos de administrador
- `is_verified`: Email verificado
- `first_name`: Nombre del usuario
- `last_name`: Apellido del usuario

### `app/schemas/user.py`

Esquemas Pydantic para validación y serialización:

```python
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str | None = None
    last_name: str | None = None

class UserRead(BaseModel):
    id: int
    email: str
    first_name: str | None
    last_name: str | None
    is_active: bool
    is_superuser: bool
    is_verified: bool
```

### `app/core/security.py`

Configuración de autenticación JWT:

```python
from fastapi_users.authentication import JWTStrategy, BearerTransport

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.SECRET_KEY, lifetime_seconds=3600)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)
```

**Características:**
- Bearer token en header `Authorization: Bearer <token>`
- Tokens JWT con expiración de 1 hora
- Estrategia de autenticación configurable

### `app/core/users.py`

Lógica de gestión de usuarios:

```python
class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET
    
    async def on_after_register(self, user: User, request=None):
        print(f"Usuario {user.email} se ha registrado.")
```

**Métodos:**
- `on_after_register`: Hook después del registro
- `on_after_forgot_password`: Hook para recuperación de contraseña
- `on_after_request_verify`: Hook para verificación de email
- `create`: Crear usuario con valores por defecto seguros

### `app/api/__init__.py`

Router principal que agrupa todos los routers:

```python
from fastapi import APIRouter
from app.api.routes import auth, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
```

### `app/api/routes/auth.py`

Endpoints de autenticación:
- `POST /auth/register` - Registrar usuario
- `POST /auth/jwt/login` - Login
- `POST /auth/jwt/logout` - Logout

### `app/api/routes/users.py`

Endpoints de gestión de usuarios:
- `GET /users` - Listar usuarios
- `GET /users/{user_id}` - Obtener usuario
- `PATCH /users/{user_id}` - Actualizar usuario
- `DELETE /users/{user_id}` - Eliminar usuario
- `GET /users/me` - Obtener usuario actual

## 🗄️ Base de Datos

### Tabla `users`

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(320) UNIQUE NOT NULL,
    hashed_password VARCHAR(1024) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    first_name VARCHAR(50),
    last_name VARCHAR(50)
);
```

### Índices

- `email` - Búsqueda rápida por email
- `id` - Clave primaria

## 🐳 Docker

### `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y gcc postgresql-client

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### `docker-compose.yml`

Orquesta dos servicios:

1. **db** - PostgreSQL 15
   - Puerto: 5432
   - Usuario: postgres
   - Contraseña: postgres
   - Base de datos: odin
   - Volumen: postgres_data

2. **fastapi-app** - Aplicación FastAPI
   - Puerto: 8000
   - Depende de: db
   - Ejecuta migraciones automáticamente

## 📦 Dependencias Principales

### Framework y Servidor
- `fastapi` - Framework web
- `uvicorn` - Servidor ASGI
- `uvloop` - Event loop de alto rendimiento

### Base de Datos
- `sqlalchemy` - ORM
- `asyncpg` - Driver PostgreSQL asincrónico
- `alembic` - Migraciones

### Autenticación
- `fastapi-users` - Sistema de autenticación
- `PyJWT` - Tokens JWT
- `argon2-cffi` - Hashing de contraseñas

### Validación
- `pydantic` - Validación de datos
- `email-validator` - Validación de emails

### Configuración
- `python-dotenv` - Variables de entorno
- `pydantic-settings` - Configuración tipada

## 🔄 Flujo de Autenticación

```
1. Usuario registra: POST /auth/register
   ↓
2. Contraseña se hashea con Argon2
   ↓
3. Usuario se crea en BD
   ↓
4. Usuario hace login: POST /auth/jwt/login
   ↓
5. Se valida email y contraseña
   ↓
6. Se genera JWT token
   ↓
7. Cliente incluye token en header: Authorization: Bearer <token>
   ↓
8. Servidor valida token en cada request
   ↓
9. Si es válido, se ejecuta el endpoint
```

## 🔐 Seguridad

### Contraseñas
- Hasheadas con Argon2 (algoritmo moderno y seguro)
- Nunca se almacenan en texto plano

### Tokens JWT
- Firmados con SECRET_KEY
- Expiración: 1 hora
- Bearer transport en header Authorization

### CORS
- Configurado para permitir todos los orígenes (ajustar en producción)

### Base de Datos
- Conexión asincrónica
- Prepared statements (previene SQL injection)

## 🚀 Escalabilidad

### Asincronía
- Todas las operaciones son asincrónicas
- Permite manejar múltiples requests concurrentes

### Event Loop
- uvloop para mejor rendimiento

### Migraciones
- Alembic para cambios de esquema seguros
- Versionado de cambios

## 📝 Convenciones

### Nombres
- Archivos: `snake_case`
- Clases: `PascalCase`
- Funciones/métodos: `snake_case`
- Constantes: `UPPER_SNAKE_CASE`

### Imports
- Imports de stdlib primero
- Imports de librerías terceras segundo
- Imports locales tercero

### Type Hints
- Usar en todas las funciones
- Usar `|` para uniones (Python 3.10+)

---

**Última actualización**: Noviembre 2025
