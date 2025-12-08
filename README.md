# Odin - API de Gestión de Usuarios con Autenticación

Odin es una API REST moderna construida con **FastAPI** que proporciona un sistema completo de autenticación, gestión de usuarios y control de roles. Diseñada para ser escalable, segura y fácil de mantener.

## 📋 Descripción del Proyecto

Odin implementa un sistema robusto de autenticación JWT con FastAPI Users, incluyendo:

- ✅ Autenticación JWT con Bearer tokens
- ✅ Gestión completa de usuarios (CRUD)
- ✅ Sistema de roles y permisos (superusuarios)
- ✅ Base de datos PostgreSQL asincrónica
- ✅ Migraciones con Alembic
- ✅ Containerización con Docker
- ✅ CORS configurado
- ✅ Documentación automática con Swagger/ReDoc

## 🛠️ Stack Tecnológico

### Backend
- **FastAPI** (0.121.3) - Framework web moderno y rápido
- **Python** (3.11) - Lenguaje de programación
- **SQLAlchemy** (2.0.44) - ORM asincrónico
- **FastAPI Users** (15.0.1) - Sistema de autenticación y gestión de usuarios
- **Pydantic** (2.12.4) - Validación de datos
- **PyJWT** (2.10.1) - Manejo de tokens JWT
- **Alembic** (1.17.2) - Migraciones de base de datos

### Base de Datos
- **PostgreSQL** (15-alpine) - Base de datos relacional
- **asyncpg** (0.30.0) - Driver asincrónico para PostgreSQL
- **psycopg2-binary** (2.9.11) - Adaptador PostgreSQL para Python

### Seguridad
- **Argon2** (23.1.0) - Hashing de contraseñas
- **bcrypt** (4.3.0) - Encriptación adicional
- **cryptography** (46.0.3) - Operaciones criptográficas

### Servidor
- **Uvicorn** (0.38.0) - Servidor ASGI
- **uvloop** (0.22.1) - Event loop de alto rendimiento (solo Linux/macOS)
- **httptools** (0.7.1) - Parseo HTTP optimizado (solo Linux/macOS)

### Utilidades
- **python-dotenv** (1.2.1) - Gestión de variables de entorno
- **pydantic-settings** (2.12.0) - Configuración basada en Pydantic
- **email-validator** (2.3.0) - Validación de emails
- **python-multipart** (0.0.20) - Manejo de multipart/form-data

## 📁 Estructura del Proyecto

```
Odin/
├── app/
│   ├── users/                   # Dominio de usuarios
│   │   ├── __init__.py
│   │   ├── models.py           # Modelo de usuario (SQLAlchemy)
│   │   ├── schemas.py          # Esquemas Pydantic para usuarios
│   │   ├── routes.py           # Endpoints de gestión de usuarios
│   │   └── services.py         # Lógica de negocio de usuarios
│   ├── auth/                    # Dominio de autenticación
│   │   ├── __init__.py
│   │   └── routes.py           # Endpoints de autenticación
│   ├── api/
│   │   └── __init__.py         # Router principal que agrupa dominios
│   ├── core/
│   │   └── security.py         # Configuración de seguridad y JWT
│   ├── models/                  # Compatibilidad con Alembic
│   │   ├── __init__.py         # Re-exporta modelos
│   │   └── user.py             # Modelo original (compatibilidad)
│   ├── schemas/                 # Compatibilidad
│   │   └── __init__.py         # Re-exporta esquemas
│   ├── config.py               # Configuración de la aplicación
│   ├── database.py             # Configuración de base de datos
│   └── main.py                 # Punto de entrada de la aplicación
├── alembic/                    # Migraciones de base de datos
├── alembic.ini                 # Configuración de Alembic
├── docker-compose.yml          # Orquestación de contenedores
├── Dockerfile                  # Imagen Docker de la aplicación
├── requirements.txt            # Dependencias de Python
├── requirements-windows.txt    # Dependencias compatibles con Windows
├── Odin_API.postman_collection.json  # Colección de Postman
└── README.md                   # Este archivo
```

## 🏗️ Arquitectura por Dominios

Odin utiliza una **arquitectura por dominios** (Domain-Driven Design) que organiza el código por funcionalidades de negocio en lugar de por tipo de archivo.

### 🎯 Ventajas de esta Arquitectura:

- **✅ Cohesión alta**: Todo relacionado con una funcionalidad está junto
- **✅ Acoplamiento bajo**: Los dominios son independientes entre sí
- **✅ Escalabilidad**: Fácil agregar nuevas funcionalidades
- **✅ Mantenibilidad**: Cambios localizados en cada dominio
- **✅ Trabajo en equipo**: Cada desarrollador puede trabajar en su dominio

### 📦 Estructura de un Dominio:

Cada dominio sigue la misma estructura consistente:

```
app/nombre_dominio/
├── __init__.py         # Paquete Python
├── models.py          # Modelos de base de datos (SQLAlchemy)
├── schemas.py         # Validación de datos (Pydantic)
├── routes.py          # Endpoints HTTP (FastAPI)
└── services.py        # Lógica de negocio
```

### 🔄 Agregar un Nuevo Dominio:

1. **Crear la estructura**:
   ```bash
   mkdir app/products
   touch app/products/{__init__.py,models.py,schemas.py,routes.py,services.py}
   ```

2. **Registrar en el router principal** (`app/api/__init__.py`):
   ```python
   from app.products.routes import router as products_router
   api_router.include_router(products_router, prefix="/products", tags=["products"])
   ```

3. **Agregar modelos a Alembic** (si es necesario) (`alembic/env.py`):
   ```python
   from app.products.models import Product
   ```

## 🚀 Instalación y Configuración

### Requisitos Previos

- **Docker** y **Docker Compose** (recomendado)
- O bien: **Python 3.11+** y **PostgreSQL 15+**

### Opción 1: Con Docker (Recomendado)

#### 1. Clonar el repositorio

```bash
git clone https://github.com/G4bomon/Odin.git
cd Odin
```

#### 2. Crear archivo `.env`

```bash
cp .env.example .env
```

O crear manualmente un archivo `.env` en la raíz del proyecto:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/odin
SECRET_KEY=tu-clave-secreta-super-segura-aqui-cambiar-en-produccion
```

#### 3. Iniciar los contenedores

```bash
docker-compose up -d
```

La aplicación estará disponible en:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

#### 4. Verificar el estado

```bash
docker-compose ps
docker-compose logs -f fastapi-app
```

### Opción 2: Instalación Local

#### 1. Clonar el repositorio

```bash
git clone https://github.com/G4bomon/Odin.git
cd Odin
```

#### 2. Crear entorno virtual

```bash
# En Windows
source venv/Scripts/activate # PARA GIT BASH 
python -m venv venv
venv\Scripts\activate

# En macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Instalar dependencias

```bash
# Windows
pip install -r requirements-windows.txt

# macOS/Linux
pip install -r requirements.txt
```

#### 4. Crear archivo `.env`

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/odin
SECRET_KEY=tu-clave-secreta-super-segura-aqui-cambiar-en-produccion
```

#### 5. Configurar PostgreSQL

```bash
# Crear base de datos (si no existe)
createdb odin
```

#### 6. Ejecutar migraciones

```bash
alembic upgrade head
```

#### 7. Iniciar el servidor

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

La aplicación estará disponible en http://localhost:8000

## 📚 Endpoints Principales

### Salud y Estado

```
GET /health
```

Verifica el estado de la API.

**Respuesta:**
```json
{
  "status": "healthy"
}
```

### Raíz

```
GET /
```

Información general de la API.

**Respuesta:**
```json
{
  "message": "API funcionando correctamente",
  "version": "1.0.0",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

### Autenticación

#### Registro de Usuario

```
POST /auth/register
```

**Body:**
```json
{
  "email": "usuario@example.com",
  "password": "contraseña_segura",
  "first_name": "Juan",
  "last_name": "Pérez"
}
```

#### Login

```
POST /auth/jwt/login
```

**Body (form-data):**
```
username: usuario@example.com
password: contraseña_segura
```

**Respuesta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Logout

```
POST /auth/jwt/logout
```

Requiere autenticación con Bearer token.

### Gestión de Usuarios

#### Obtener Usuario Actual

```
GET /users/me
```

Requiere autenticación con Bearer token.

**Respuesta:**
```json
{
  "id": 1,
  "email": "usuario@example.com",
  "first_name": "Juan",
  "last_name": "Pérez",
  "is_active": true,
  "is_superuser": false,
  "is_verified": false
}
```

#### Actualizar Usuario Actual

```
PATCH /users/me
```

Requiere autenticación con Bearer token.

**Body:**
```json
{
  "first_name": "Juan",
  "last_name": "Pérez"
}
```

#### Listar Todos los Usuarios

```
GET /users
```

Requiere autenticación con Bearer token.

**Respuesta:**
```json
[
  {
    "id": 1,
    "email": "usuario@example.com",
    "first_name": "Juan",
    "last_name": "Pérez",
    "is_active": true,
    "is_superuser": false,
    "is_verified": false
  }
]
```

#### Obtener Usuario por ID

```
GET /users/{user_id}
```

Requiere autenticación con Bearer token.

#### Actualizar Usuario por ID

```
PATCH /users/{user_id}
```

Requiere autenticación con Bearer token (solo superusuarios).

#### Eliminar Usuario

```
DELETE /users/{user_id}
```

Requiere autenticación con Bearer token (solo superusuarios).

## 🔐 Autenticación y Seguridad

### JWT (JSON Web Tokens)

La API utiliza JWT para autenticación stateless:

1. El usuario se registra o hace login
2. Recibe un `access_token` JWT
3. Incluye el token en el header `Authorization: Bearer <token>`
4. El servidor valida el token en cada solicitud

### Hashing de Contraseñas

Las contraseñas se hashean usando **Argon2**, un algoritmo moderno y seguro.

### Roles y Permisos

- **Usuario Regular**: Acceso limitado a sus propios datos
- **Superusuario**: Acceso completo a toda la API

## 🐳 Comandos Docker Útiles

```bash
# Ver logs de la aplicación
docker-compose logs -f fastapi-app

# Ver logs de la base de datos
docker-compose logs -f db

# Acceder a la shell de PostgreSQL
docker-compose exec db psql -U postgres -d odin

# Detener los contenedores
docker-compose down

# Detener y eliminar volúmenes (CUIDADO: elimina datos)
docker-compose down -v

# Reconstruir la imagen
docker-compose build --no-cache

# Ejecutar migraciones manualmente
docker-compose exec fastapi-app alembic upgrade head

# Ver estado de los contenedores
docker-compose ps
```

## 📝 Variables de Entorno

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `DATABASE_URL` | URL de conexión a PostgreSQL | `postgresql+asyncpg://postgres:postgres@db:5432/odin` |
| `SECRET_KEY` | Clave secreta para JWT | `tu-clave-super-segura` |

**⚠️ Importante**: En producción, cambiar `SECRET_KEY` a una cadena aleatoria y segura.

## 📦 Archivos de Requisitos

El proyecto incluye múltiples archivos de requisitos para diferentes plataformas:

| Archivo | Plataforma | Descripción |
|---------|-----------|-------------|
| `requirements.txt` | macOS/Linux | Dependencias estándar sin optimizaciones específicas |
| `requirements-windows.txt` | Windows | Dependencias compatibles con Windows (sin `uvloop` ni `httptools`) |

**Nota**: `uvloop` y `httptools` no son compatibles con Windows, por lo que se excluyen del archivo `requirements-windows.txt`. Estas librerías optimizan el rendimiento en sistemas Unix-like, pero no son esenciales para el funcionamiento de la API.

## 🔄 Migraciones de Base de Datos

### Crear una nueva migración

```bash
alembic revision --autogenerate -m "Descripción del cambio"
```

### Aplicar migraciones

```bash
alembic upgrade head
```

### Ver historial de migraciones

```bash
alembic history
```

### Revertir a una versión anterior

```bash
alembic downgrade -1
```

## 🧪 Testing (Próximo)

Se recomienda agregar tests unitarios e integración usando `pytest`.

## 📖 Documentación y Testing

### 🌐 Documentación Interactiva

Una vez que la API esté corriendo, accede a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 📮 Colección de Postman

El proyecto incluye una colección completa de Postman para probar todos los endpoints:

1. **Importar en Postman**: 
   - File → Import → Seleccionar `Odin_API.postman_collection.json`

2. **Flujo de pruebas recomendado**:
   - Health Check → Register User → Login → Get Current User

3. **Variables automáticas**:
   - Los tokens JWT se guardan automáticamente
   - Variables de entorno preconfiguradas
   - Scripts de prueba incluidos

### 🧪 Endpoints Disponibles

- **Health**: `GET /health` - Estado de la API
- **Auth**: `POST /auth/register`, `POST /auth/jwt/login`, `POST /auth/jwt/logout`
- **Users**: `GET /users/me`, `PATCH /users/me`, `GET /users/{id}`

## 🤝 Contribuciones

1. Crear una rama para tu feature: `git checkout -b feature/AmazingFeature`
2. Commit tus cambios: `git commit -m 'Add some AmazingFeature'`
3. Push a la rama: `git push origin feature/AmazingFeature`
4. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

Para reportar bugs o solicitar features, abre un issue en el repositorio.

---

**Última actualización**: Noviembre 2025
