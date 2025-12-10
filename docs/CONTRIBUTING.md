# 🤝 Guía de Contribuciones - Odin

Gracias por tu interés en contribuir a Odin. Este documento proporciona directrices para contribuir al proyecto.

## 📋 Antes de Comenzar

1. Asegúrate de tener instalado:
   - Git
   - Python 3.11+
   - Docker y Docker Compose (recomendado)
   - PostgreSQL 15+ (si no usas Docker)

2. Fork el repositorio y clona tu fork:

```bash
git clone https://github.com/TU_USUARIO/Odin.git
cd Odin
git remote add upstream https://github.com/G4bomon/Odin.git
```

## 🔧 Configuración del Entorno de Desarrollo

### 1. Crear rama de feature

```bash
git checkout -b feature/nombre-descriptivo
```

### 2. Instalar dependencias

```bash
# Con Docker
docker-compose up -d

# O localmente
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Crear archivo .env

```bash
cp .env.example .env
```

## 📝 Estándares de Código

### Python

- Seguir [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Usar type hints en todas las funciones
- Máximo 88 caracteres por línea (Black formatter)
- Docstrings en español para métodos públicos

### Ejemplo de función bien formateada

```python
async def create_user(
    email: str,
    password: str,
    first_name: str | None = None,
    last_name: str | None = None,
) -> User:
    """
    Crear un nuevo usuario en la base de datos.
    
    Args:
        email: Correo electrónico del usuario
        password: Contraseña sin hashear
        first_name: Nombre del usuario (opcional)
        last_name: Apellido del usuario (opcional)
    
    Returns:
        Usuario creado
    
    Raises:
        ValueError: Si el email ya existe
    """
    # Implementación
    pass
```

## 🧪 Testing

### Ejecutar tests

```bash
# Instalar pytest
pip install pytest pytest-asyncio

# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=app
```

### Escribir tests

```python
import pytest
from app.models.user import User

@pytest.mark.asyncio
async def test_create_user():
    """Test para crear un usuario"""
    user = await create_user(
        email="test@example.com",
        password="password123"
    )
    assert user.email == "test@example.com"
    assert user.is_active is True
```

## 📦 Migraciones de Base de Datos

Si modificas modelos, crea una migración:

```bash
# Generar migración automática
alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Ver historial
alembic history
```

## 🔄 Flujo de Contribución

### 1. Hacer cambios

```bash
# Editar archivos
# Asegúrate de seguir los estándares de código
```

### 2. Commit

```bash
git add .
git commit -m "feat: descripción clara del cambio"
```

**Formato de mensaje de commit:**
- `feat:` Nueva funcionalidad
- `fix:` Corrección de bug
- `docs:` Cambios en documentación
- `refactor:` Refactorización de código
- `test:` Agregar o modificar tests
- `chore:` Cambios en configuración

### 3. Push

```bash
git push origin feature/nombre-descriptivo
```

### 4. Pull Request

1. Ve a GitHub y abre un Pull Request
2. Describe claramente qué cambios hiciste
3. Referencia cualquier issue relacionado (#123)
4. Espera revisión

**Plantilla de PR:**

```markdown
## Descripción
Breve descripción de los cambios

## Tipo de cambio
- [ ] Bug fix
- [ ] Nueva funcionalidad
- [ ] Breaking change
- [ ] Cambio en documentación

## Cambios realizados
- Cambio 1
- Cambio 2

## Testing
- [ ] He probado los cambios localmente
- [ ] He agregado tests
- [ ] Los tests pasan

## Checklist
- [ ] Mi código sigue los estándares del proyecto
- [ ] He actualizado la documentación
- [ ] No hay warnings o errores
```

## 🐛 Reportar Bugs

Abre un issue con:

1. **Título descriptivo**
2. **Descripción clara** del problema
3. **Pasos para reproducir**
4. **Comportamiento esperado**
5. **Comportamiento actual**
6. **Entorno** (OS, Python version, etc.)

**Plantilla:**

```markdown
## Descripción
Descripción clara del bug

## Pasos para reproducir
1. Paso 1
2. Paso 2
3. Paso 3

## Comportamiento esperado
Qué debería pasar

## Comportamiento actual
Qué está pasando

## Entorno
- OS: Windows/macOS/Linux
- Python: 3.11
- Docker: Sí/No
```

## 💡 Sugerir Mejoras

Abre un issue con:

1. **Descripción clara** de la mejora
2. **Justificación** de por qué es útil
3. **Ejemplos** de cómo se usaría

## 📚 Documentación

- Actualiza el `README.md` si cambias funcionalidad
- Agrega docstrings a nuevas funciones
- Documenta cambios en `CHANGELOG.md` (si existe)

## 🚀 Proceso de Release

Los maintainers seguirán este proceso:

1. Crear rama `release/vX.Y.Z`
2. Actualizar versión en archivos relevantes
3. Actualizar CHANGELOG
4. Crear PR para revisión
5. Merge a `main` y crear tag
6. Deploy a producción

## 📞 Contacto

- Issues: GitHub Issues
- Discussions: GitHub Discussions
- Email: contacto@proyecto.com

## ✨ Código de Conducta

Por favor, sé respetuoso y profesional. Nos comprometemos a proporcionar un ambiente acogedor para todos.

---

**¡Gracias por contribuir a Odin!** 🎉
