# 🔐 Guía del Sistema de Roles en Odin

## Descripción General

Odin implementa un sistema de roles jerárquico que permite controlar el acceso a diferentes funcionalidades de la API. Los roles están organizados en una jerarquía donde los roles superiores tienen todos los permisos de los roles inferiores.

## Roles Disponibles

### 1. SUPERADMIN (Nivel 4)

- **Descripción**: Acceso total a la aplicación
- **Permisos**:
  - Gestionar todos los usuarios
  - Asignar roles a otros usuarios
  - Crear y eliminar empresas
  - Acceder a todos los datos
  - Gestionar permisos y roles

### 2. ADMIN (Nivel 3)

- **Descripción**: Gestión de empresas y usuarios
- **Permisos**:
  - Listar usuarios por rol
  - Gestionar empresas
  - Acceder a reportes
  - Hereda todos los permisos de EMPRESA y USUARIO

### 3. EMPRESA (Nivel 2)

- **Descripción**: Gestión de su propia empresa y datos
- **Permisos**:
  - Gestionar datos de su empresa
  - Crear y editar productos
  - Ver reportes de su empresa
  - Hereda todos los permisos de USUARIO

### 4. USUARIO (Nivel 1)

- **Descripción**: Usuario regular con acceso limitado
- **Permisos**:
  - Ver su propio perfil
  - Editar su información personal
  - Acceso a funcionalidades básicas

## Jerarquía de Roles

```
SUPERADMIN (4)
    ↓
  ADMIN (3)
    ↓
  EMPRESA (2)
    ↓
  USUARIO (1)
```

Un usuario con rol ADMIN puede hacer todo lo que puede hacer un EMPRESA, y un EMPRESA puede hacer todo lo que puede hacer un USUARIO.

## Uso en Endpoints

### Proteger un Endpoint con Rol Específico

```python
from fastapi import APIRouter, Depends
from app.core.security import require_admin, require_role, require_superadmin
from app.core.roles import RoleEnum
from app.users.models import User

router = APIRouter()

# Solo ADMIN o superior
@router.get("/admin-only")
async def admin_endpoint(user: User = Depends(require_admin)):
    return {"message": f"Hola {user.email}"}

# Solo SUPERADMIN
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    user: User = Depends(require_superadmin)
):
    # Lógica para eliminar usuario
    pass

# Solo EMPRESA o superior
@router.get("/empresa/dashboard")
async def empresa_dashboard(user: User = Depends(require_role(RoleEnum.EMPRESA))):
    return {"message": "Dashboard de empresa"}
```

### Permitir Múltiples Roles

```python
from app.core.security import require_any_role

@router.get("/content")
async def get_content(
    user: User = Depends(require_any_role([RoleEnum.ADMIN, RoleEnum.EMPRESA]))
):
    return {"message": "Contenido para ADMIN o EMPRESA"}
```

### Verificación Manual en Lógica

```python
from app.core.roles import has_role, RoleEnum

async def some_function(user: User):
    if has_role(user.role, RoleEnum.ADMIN):
        # El usuario es ADMIN o superior
        # Hacer algo especial
        pass
    else:
        # El usuario es EMPRESA o USUARIO
        pass
```

## Endpoints de Gestión de Roles

### Obtener Información de Roles

```
GET /roles/info
```

Devuelve información sobre todos los roles disponibles.

**Respuesta:**

```json
{
  "superadmin": {
    "role": "superadmin",
    "description": "Acceso total a la aplicación. Puede gestionar todo.",
    "hierarchy_level": 4
  },
  "admin": {
    "role": "admin",
    "description": "Gestión de empresas y usuarios. Acceso administrativo.",
    "hierarchy_level": 3
  },
  ...
}
```

### Obtener Jerarquía de Roles

```
GET /roles/hierarchy
```

Devuelve la jerarquía numérica de roles.

**Respuesta:**

```json
{
  "hierarchy": {
    "superadmin": 4,
    "admin": 3,
    "empresa": 2,
    "usuario": 1
  },
  "description": "Número mayor = más permisos"
}
```

### Asignar Rol a Usuario

```
POST /roles/assign
```

**Requiere**: SUPERADMIN

**Body:**

```json
{
  "user_id": 5,
  "role": "admin"
}
```

**Respuesta:**

```json
{
  "id": 5,
  "email": "usuario@example.com",
  "first_name": "Juan",
  "last_name": "Pérez",
  "role": "admin",
  "is_active": true,
  "is_verified": false
}
```

### Listar Usuarios por Rol

```
GET /roles/users?role=admin&skip=0&limit=100
```

**Requiere**: ADMIN o superior

**Respuesta:**

```json
[
  {
    "id": 1,
    "email": "admin@example.com",
    "role": "admin",
    ...
  }
]
```

### Obtener Mi Rol

```
GET /roles/my-role
```

**Requiere**: Autenticación

**Respuesta:**

```json
{
  "user_id": 5,
  "email": "usuario@example.com",
  "role": "empresa",
  "hierarchy_level": 2
}
```

### Crear Permiso para Rol

```
POST /roles/permissions
```

**Requiere**: SUPERADMIN

**Body:**

```json
{
  "role": "admin",
  "permission": "users.delete",
  "description": "Permiso para eliminar usuarios"
}
```

### Obtener Permisos de Rol

```
GET /roles/permissions?role=admin
```

**Requiere**: Autenticación

**Respuesta:**

```json
[
  {
    "id": 1,
    "role": "admin",
    "permission": "users.delete",
    "description": "Permiso para eliminar usuarios",
    "created_at": "2025-01-15T10:30:00Z"
  }
]
```

## Crear un Usuario con Rol Específico

### Registro Normal (Rol USUARIO por defecto)

```
POST /auth/register
```

**Body:**

```json
{
  "email": "usuario@example.com",
  "password": "password123",
  "first_name": "Juan",
  "last_name": "Pérez"
}
```

El usuario se creará con rol `USUARIO` por defecto.

### Asignar Rol Diferente

Después de crear el usuario, un SUPERADMIN debe usar el endpoint `/roles/assign` para cambiar el rol.

## Ejemplos de Uso

### Ejemplo 1: Endpoint Solo para Administradores

```python
from fastapi import APIRouter, Depends, HTTPException
from app.core.security import require_admin
from app.users.models import User

router = APIRouter()

@router.get("/admin/statistics")
async def get_statistics(user: User = Depends(require_admin)):
    """
    Obtiene estadísticas del sistema.
    Solo accesible para ADMIN o SUPERADMIN.
    """
    return {
        "total_users": 150,
        "active_users": 120,
        "total_revenue": 50000
    }
```

### Ejemplo 2: Endpoint para Empresas

```python
@router.get("/empresa/products")
async def get_empresa_products(user: User = Depends(require_role(RoleEnum.EMPRESA))):
    """
    Obtiene los productos de la empresa del usuario.
    Solo accesible para EMPRESA, ADMIN o SUPERADMIN.
    """
    # Lógica para obtener productos de la empresa
    pass
```

### Ejemplo 3: Verificación Condicional

```python
@router.get("/data")
async def get_data(user: User = Depends(current_active_user)):
    """
    Devuelve datos diferentes según el rol del usuario.
    """
    from app.core.roles import has_role, RoleEnum

    if has_role(user.role, RoleEnum.ADMIN):
        # Devolver datos completos
        return {"data": "todos los datos"}
    elif has_role(user.role, RoleEnum.EMPRESA):
        # Devolver datos de la empresa
        return {"data": "datos de la empresa"}
    else:
        # Devolver datos del usuario
        return {"data": "mis datos"}
```

## Migración de Base de Datos

Para agregar el sistema de roles a una base de datos existente:

```bash
# Crear migración automática
alembic revision --autogenerate -m "Add roles system"

# Aplicar migración
alembic upgrade head
```

## Consideraciones de Seguridad

1. **Nunca permitir que un usuario cambie su propio rol** - Solo SUPERADMIN puede asignar roles
2. **Validar roles en el backend** - No confiar en información del cliente
3. **Usar HTTPS en producción** - Los tokens JWT deben transmitirse de forma segura
4. **Rotar SECRET_KEY regularmente** - Cambiar la clave secreta periódicamente
5. **Auditar cambios de rol** - Registrar quién cambió el rol de quién y cuándo

## Extensión Futura

El sistema está diseñado para ser extensible. Se pueden agregar:

- **Permisos granulares**: Más allá de roles, permisos específicos por usuario
- **Grupos de usuarios**: Agrupar usuarios y asignar permisos a grupos
- **Auditoría**: Registrar todos los cambios de roles y permisos
- **Roles personalizados**: Permitir crear roles personalizados

## Troubleshooting

### Error: "Se requiere rol ADMIN o superior"

- Verifica que el usuario tenga el rol correcto
- Usa `GET /roles/my-role` para verificar tu rol actual
- Solicita a un SUPERADMIN que te asigne el rol correcto

### Error: "Se requiere rol SUPERADMIN"

- Solo SUPERADMIN puede ejecutar esta acción
- Contacta al administrador del sistema

### El rol no se actualiza

- Verifica que hayas usado el endpoint `/roles/assign` correctamente
- Asegúrate de que el usuario_id sea válido
- Verifica que tengas permisos de SUPERADMIN
