# 🚀 Guía Rápida de Inicio - Odin

## Inicio Rápido con Docker (Recomendado)

### 1️⃣ Clonar y Configurar

```bash
git clone https://github.com/G4bomon/Odin.git
cd Odin
cp .env.example .env
```

### 2️⃣ Iniciar la Aplicación

```bash
docker-compose up -d
```

### 3️⃣ Verificar que está funcionando

```bash
# Ver logs
docker-compose logs -f fastapi-app

# Verificar salud
curl http://localhost:8000/health
```

### 4️⃣ Acceder a la API

- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Inicio Rápido Local (Sin Docker)

### 1️⃣ Clonar y Entorno Virtual

```bash
git clone https://github.com/G4bomon/Odin.git
cd Odin

# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2️⃣ Instalar Dependencias

```bash
# Windows
pip install -r requirements-windows.txt

# macOS/Linux
pip install -r requirements.txt
```

### 3️⃣ Configurar Base de Datos

```bash
# Crear archivo .env
cp .env.example .env

# Editar .env y cambiar:
# DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/odin

# Crear base de datos (si no existe)
createdb odin

# Ejecutar migraciones
alembic upgrade head
```

### 4️⃣ Iniciar el Servidor

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🧪 Prueba Rápida de Endpoints

### Registrar Usuario

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "first_name": "Test",
    "last_name": "User"
  }'
```

### Login

```bash
curl -X POST "http://localhost:8000/auth/jwt/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=password123"
```

### Obtener Usuario Actual

```bash
curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🐳 Comandos Docker Útiles

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Detener contenedores
docker-compose down

# Reconstruir imágenes
docker-compose build --no-cache

# Acceder a PostgreSQL
docker-compose exec db psql -U postgres -d odin

# Ejecutar migraciones
docker-compose exec fastapi-app alembic upgrade head
```

---

## ⚙️ Configuración Importante

### Variables de Entorno (.env)

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/odin
SECRET_KEY=tu-clave-secreta-super-segura
```

**⚠️ En producción:**
- Cambiar `SECRET_KEY` a una cadena aleatoria segura
- Cambiar credenciales de PostgreSQL
- Ajustar CORS según sea necesario

---

## 📚 Documentación Completa

Ver `README.md` para documentación detallada, endpoints, y más información.

---

## 🆘 Problemas Comunes

### Puerto 5432 ya está en uso

```bash
# Cambiar puerto en docker-compose.yml
# Línea: - "5432:5432"
# Cambiar a: - "5433:5432"
```

### Migraciones no se ejecutan

```bash
# Ejecutar manualmente
docker-compose exec fastapi-app alembic upgrade head
```

### Base de datos no se conecta

```bash
# Verificar que PostgreSQL está corriendo
docker-compose ps

# Ver logs de la BD
docker-compose logs db
```

---

**¿Necesitas ayuda?** Abre un issue en el repositorio.
