# AGENTS.md

Guía de contexto, arquitectura y convenciones para agentes de IA que trabajen en **TP2-FastApi-Biblioteca**.

## Descripción del Proyecto

API RESTful desarrollada para gestionar las operaciones de una biblioteca (**Trabajo Práctico Nº 2 — Programación IV, UTN Paraná**). Permite administrar **autores**, **libros**, **socios** y **préstamos** (incluyendo control de stock, fechas de vencimiento, devoluciones y cálculo de multas).

## Stack Tecnológico

- **Lenguaje**: Python 3.14+
- **Framework Web**: FastAPI (`fastapi`, `fastapi-cli`, `uvicorn`)
- **ORM y Validación**: SQLModel (sobre SQLAlchemy 2.x y Pydantic v2)
- **Base de Datos**: SQLite (`database.db` en entorno local; en memoria para tests)
- **Testing**: `pytest`, `pytest-cov`, `httpx` (`fastapi.testclient.TestClient`)

## Comandos de Entorno, Ejecución y Testing

El proyecto utiliza un entorno virtual local en `.venv/`.

```powershell
# Activar entorno virtual (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Levantar el servidor de desarrollo (con recarga automática)
fastapi dev main.py
# Alternativa con Uvicorn:
uvicorn main:app --reload

# Ejecutar sin activar el entorno virtual explícitamente
.\.venv\Scripts\python.exe -m fastapi dev main.py

# Ejecutar suite de pruebas
pytest

# Ejecutar pruebas con reporte de cobertura
pytest --cov=.
```

- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

## Arquitectura y Estructura del Proyecto

El proyecto sigue estrictamente una **arquitectura en capas** con separación de responsabilidades:

```text
TP2-FastApi-Biblioteca/
├── main.py                      # Punto de entrada FastAPI, registro de routers, ciclo de vida y seed inicial
├── api/                         # Capa de Presentación / Controladores HTTP
│   ├── payload/                 # Esquemas DTO de entrada/salida (Create, Update, Response)
│   ├── autor_controller.py      # Endpoints de autores
│   ├── libro_controller.py      # Endpoints de libros
│   └── socio_controller.py      # Endpoints de socios (y/o controlador de préstamos)
├── services/                    # Capa de Lógica de Negocio y reglas de dominio
├── repositories/                # Capa de Acceso a Datos (persistencia)
│   └── database.py              # Configuración del engine SQLite, create_db_and_tables() y get_session()
└── models/                      # Entidades de dominio y modelos de tabla SQLModel
    ├── autor.py                 # Autor y AutorDB (tabla: autores)
    ├── libro.py                 # Libro y LibroDB (tabla: libros)
    ├── libro_autor.py           # LibroAutorLink (tabla intermedia N:N)
    ├── socio.py                 # Socio y SocioDB (tabla: socios)
    └── prestamo.py              # Prestamo y PrestamoDB (tabla: prestamos)
```

### Responsabilidades por Capa

1. **Controladores (`api/`)**:
   - Definen instancias de `APIRouter` con prefijos y `tags` claros (ej. `prefix="/libros"`, `tags=["Libros"]`).
   - Reciben y retornan DTOs definidos en `api/payload/` (o modelos base sin relaciones cíclicas).
   - Gestionan códigos de estado HTTP (`status.HTTP_201_CREATED`, `status.HTTP_204_NO_CONTENT`, etc.) y traducen errores de dominio a `HTTPException`.
   - **Prohibido** escribir consultas SQLModel (`select`, `session.add`, `session.commit`) directamente en los controladores.
2. **Servicios (`services/`)**:
   - Implementan las reglas de negocio (disponibilidad de stock al prestar, validación de socio activo, unicidad de ISBN/email, cálculo de multas por mora en devoluciones, etc.).
   - Coordinan llamadas a uno o más repositorios.
3. **Repositorios (`repositories/`)**:
   - Única capa autorizada a interactuar directamente con `Session` de SQLModel (`session.exec(select(...))`, `session.get(...)`, `session.add(...)`, `session.commit()`, `session.refresh(...)`).
4. **Modelos (`models/`)**:
   - Definen la estructura base con validaciones `Field(...)` y las clases persistentes `*DB(..., table=True)` con `__tablename__` explícito y relaciones `Relationship(...)`.

## Modelo de Dominio

- **Autor (`AutorDB` — tabla `autores`)**: `id`, `nombre` (3–100 caracteres), `nacionalidad` (opcional). Relación **N:N** con `LibroDB` a través de `LibroAutorLink`.
- **Libro (`LibroDB` — tabla `libros`)**: `id`, `titulo` (4–72 caracteres), `anio` (1900–2026, opcional), `isbn` (10–17 caracteres, único e indexado), `stock` (`>= 0`). Relación **N:N** con `AutorDB` y **1:N** con `PrestamoDB`.
- **Socio (`SocioDB` — tabla `socios`)**: `id`, `nombre` (3–100 caracteres), `email` (único e indexado), `activo` (`bool`, por defecto `True`). Relación **1:N** con `PrestamoDB`.
- **Préstamo (`PrestamoDB` — tabla `prestamos`)**: `id`, `socio_id` (`FK -> socios.id`), `libro_id` (`FK -> libros.id`), `fecha_prestamo`, `fecha_vencimiento`, `fecha_devolucion` (opcional), `multa` (`>= 0.0`).

## Convenciones de Código y Estilo

- **Idioma**: Mantener nombres de clases, variables, endpoints, comentarios y mensajes de error de dominio en **español**, evitando caracteres no ASCII en identificadores Python (usar `anio` en vez de `año`, `prestamo` en vez de `préstamo`).
- **Estilo y Tipado (PEP 8 + Python 3.14)**:
  - Incluir anotaciones de tipo completas usando sintaxis moderna (`str | None`, `list[LibroDB]`, `Generator[Session, None, None]`).
  - No utilizar punto y coma (`;`) al final de las sentencias en Python.
  - Módulos, funciones y variables en `snake_case`; clases en `PascalCase`.
- **Patrones SQLModel y Prevención de Errores Comunes**:
  - Usar `from typing import TYPE_CHECKING` junto con anotaciones entre comillas (`list["LibroDB"]`) para evitar **importaciones circulares** entre archivos de `models/`.
  - Asegurar que toda clave foránea (`Field(foreign_key="...")`) coincida exactamente con el `__tablename__` de la clase `*DB` destino (`autores.id`, `libros.id`, `socios.id`, `prestamos.id`).
  - Utilizar `session.exec(select(...))` propio de SQLModel en lugar de `session.query(...)` legado de SQLAlchemy 1.x.
  - Separar los esquemas de entrada/salida (`api/payload/`) de los modelos `table=True` para no exponer relaciones perezosas ni provocar recursión infinita al serializar JSON.
- **Patrones FastAPI**:
  - Inyectar la sesión de base de datos con `Depends(get_session)` desde `repositories/database.py`.
  - Declarar `response_model` y `status_code` explícitos en cada ruta.
  - Preferir el gestor de contexto `lifespan` de FastAPI sobre `@app.on_event("startup")` al trabajar en el ciclo de vida de `main.py`.

## Lineamientos de Testing

- Ubicar las pruebas en un directorio `tests/` con archivos `test_<modulo>.py`.
- Configurar una base de datos SQLite en memoria (`sqlite://` con `connect_args={"check_same_thread": False}` y `StaticPool`) sobreescribiendo `app.dependency_overrides[get_session]` en fixtures de `pytest` (`conftest.py`), garantizando aislamiento entre tests y sin alterar `database.db`.
- Cubrir operaciones exitosas (200/201/204), errores de validación de entrada (422), recursos inexistentes (404) y violaciones de reglas de negocio (400/409, ej. préstamo sin stock disponible o ISBN duplicado).

## Reglas Operativas para Agentes

- **Respetar las capas**: Nunca saltear capas (Ruta -> Servicio -> Repositorio -> Base de Datos).
- **Verificación antes de finalizar**: Comprobar que la aplicación importe sin errores (`.\.venv\Scripts\python.exe -c "import main"`) y ejecutar `pytest` tras realizar cambios en lógica o modelos.
- **Higiene del repositorio**: No versionar ni subir archivos temporales o locales (`database.db`, `.venv/`, `__pycache__/`, `.pytest_cache/`).
- **Alcance controlado**: Realizar cambios enfocados únicamente en lo solicitado, preservando contratos existentes y documentando decisiones relevantes cuando corresponda.
