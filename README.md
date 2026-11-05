# TP2 - API de Gestión de Biblioteca

API RESTful desarrollada para la gestión integral de una biblioteca (autores, libros, socios y préstamos), desarrollada en el marco del **Trabajo Práctico Nº 2 de Programación IV — Universidad Tecnológica Nacional (UTN), Facultad Regional Paraná**.

---

## 📋 Información Académica

- **Institución:** Universidad Tecnológica Nacional – Facultad Regional Paraná (UTN FRP)
- **Cátedra:** Programación IV
- **Trabajo Práctico:** Nº 2 — FastAPI & SQLModel

---

## 🛠️ Stack Tecnológico

- **Lenguaje:** Python 3.10+ (desarrollado y probado en Python 3.14)
- **Framework Web:** [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/)
- **ORM y Modelado:** [SQLModel](https://sqlmodel.tiangolo.com/) (integración de SQLAlchemy 2.x y Pydantic v2)
- **Validación de Datos:** Pydantic v2 + `email-validator`
- **Base de Datos:** SQLite (`database.db` en local; en memoria con `StaticPool` para tests)
- **Testing:** [pytest](https://docs.pytest.org/), `pytest-cov`, [HTTPX](https://www.python-httpx.org/) (167 tests, ~98% cobertura)

---

## 🚀 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:
- **Python 3.10** o superior (puedes verificarlo con `python --version`).
- **Git** (opcional, para clonar el repositorio).

---

## ⚙️ Instalación y Configuración del Entorno

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/TP2-FastApi-Biblioteca.git
cd TP2-FastApi-Biblioteca
```

### 2. Crear el entorno virtual (`venv`)
Se recomienda aislar las dependencias del proyecto creando un entorno virtual:

- **En Windows:**
  ```powershell
  python -m venv .venv
  ```
- **En Linux / macOS:**
  ```bash
  python3 -m venv .venv
  ```

### 3. Activar el entorno virtual

- **En Windows (PowerShell):**
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
  *(Si PowerShell restringe la ejecución de scripts, ejecutar previamente: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

- **En Windows (Símbolo del sistema / CMD):**
  ```cmd
  .\.venv\Scripts\activate.bat
  ```

- **En Linux / macOS (Bash/Zsh):**
  ```bash
  source .venv/bin/activate
  ```

### 4. Instalar las dependencias
Con el entorno virtual activado, instala todas las dependencias requeridas:
```bash
pip install -r requirements.txt
```

---

## ▶️ Ejecución de la Aplicación

Para iniciar el servidor de desarrollo con recarga automática:

```bash
fastapi dev main.py
```

*Alternativa directa con Uvicorn:*
```bash
uvicorn main:app --reload
```

*O sin activar el entorno virtual previamente (Windows PowerShell):*
```powershell
.\.venv\Scripts\python.exe -m fastapi dev main.py
```

El servidor estará escuchando en `http://127.0.0.1:8000`.

### 📖 Documentación Interactiva de la API
Una vez iniciado el servidor, puedes explorar y probar todos los endpoints desde el navegador:

- **Swagger UI (OpenAPI):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🗄️ Base de Datos y Datos Semilla (Seed)

Al iniciar el servidor por primera vez, FastAPI ejecuta automáticamente el evento de inicio (`on_startup`) que:
1. Crea las tablas en la base de datos local SQLite (`database.db`).
2. Puebla datos semilla iniciales de prueba (si la base está vacía):
   - **3 Autores:** Jorge Luis Borges, Julio Cortázar, Gabriel García Márquez.
   - **3 Libros con autores asociados:** *El Aleph* (Stock: 5), *Rayuela* (Stock: 3), *Cien años de soledad* (Stock: 4).
   - **3 Socios:** Juan Pérez (Activo), María López (Activo), Carlos Gómez (Inactivo).
   - **3 Préstamos:**
     - Préstamo activo dentro de plazo (Socio 1, Libro 1).
     - Préstamo devuelto con 2 días de atraso y multa de $200 (Socio 1, Libro 2).
     - Préstamo activo vencido (Socio 2, Libro 3).

### ¿Cómo reiniciar la base de datos a su estado inicial?
Para volver a generar la base de datos con los datos semilla limpios:
1. Detén el servidor (`Ctrl + C`).
2. Elimina el archivo `database.db`:
   - En Windows (PowerShell): `Remove-Item database.db`
   - En Linux/macOS: `rm database.db`
3. Vuelve a iniciar el servidor (`fastapi dev main.py`).

---

## 🧪 Ejecución de Pruebas (Testing)

El proyecto cuenta con una suite integral de **167 pruebas automatizadas** que cubren repositorios, servicios y controladores HTTP, alcanzando aproximadamente un **98% de cobertura de código**.

> [!NOTE]
> Las pruebas utilizan una base de datos SQLite en memoria aislada (`StaticPool`), por lo que **no alteran ni dependen** de tu archivo local `database.db`.

### 1. Ejecutar toda la suite de pruebas
```bash
pytest
```
*Con salida detallada:*
```bash
pytest -v
```

### 2. Ejecutar con reporte de cobertura de código
```bash
pytest --cov=.
```
*Con reporte detallado línea por línea:*
```bash
pytest --cov=. --cov-report=term-missing
```

### 3. Ejecutar pruebas por capa específica
- **Controladores / Endpoints HTTP:**
  ```bash
  pytest tests/api/
  ```
- **Servicios / Reglas de negocio:**
  ```bash
  pytest tests/services/
  ```
- **Repositorios / Acceso a datos:**
  ```bash
  pytest tests/repositories/
  ```

---

## 🔒 Control de Acceso por Roles (Headers HTTP)

Se implementó el opcional de roles mediante cabeceras HTTP nativas sin requerir formularios de login ni passwords:

| Cabecera | Valores Permitidos | Descripción |
| :--- | :--- | :--- |
| `X-Rol` | `bibliotecario` \| `socio` | Rol del solicitante. Por defecto es `socio` si se omite. |
| `X-Socio-Id` | `<int>` (ej. `1`) | ID del socio actual. Obligatorio si `X-Rol: socio` al consultar sus préstamos. |

### Reglas de Permisos:
- **Operaciones de Catálogo y Administración:**
  - Crear, editar o eliminar autores, libros y socios requiere `X-Rol: bibliotecario` (`403 Forbidden` si lo intenta un `socio`).
  - Asociar autores a libros (`POST /libros/{id}/autores/{autor_id}`) requiere rol `bibliotecario`.
  - Registrar préstamos y devoluciones requiere rol `bibliotecario`.
- **Lectura Pública:**
  - `GET /libros` y `GET /autores` están disponibles públicamente sin restricción de rol.
- **Privacidad del Socio:**
  - Al consultar `GET /socios/{id}/prestamos`:
    - Si `X-Rol: socio`, solo puede consultar sus propios préstamos (`X-Socio-Id` debe coincidir con `{id}`). De lo contrario recibe `403 Forbidden`.
    - Si `X-Rol: bibliotecario`, puede consultar los préstamos de cualquier socio.
  - Al consultar `GET /prestamos`:
    - El `bibliotecario` obtiene el listado completo de préstamos.
    - El `socio` solo obtiene sus propios préstamos.

### Ejemplos de uso con cURL:

- **Crear un autor (requiere rol bibliotecario):**
  ```bash
  curl -X POST "http://127.0.0.1:8000/autores" \
       -H "Content-Type: application/json" \
       -H "X-Rol: bibliotecario" \
       -d '{"nombre": "Adolfo Bioy Casares", "nacionalidad": "Argentino"}'
  ```

- **Consultar préstamos propios como socio:**
  ```bash
  curl -X GET "http://127.0.0.1:8000/socios/1/prestamos" \
       -H "X-Rol: socio" \
       -H "X-Socio-Id: 1"
  ```

---

## 🏛️ Arquitectura del Proyecto

El proyecto implementa una estricta **arquitectura en capas** con inyección de dependencias centralizada:

```text
TP2-FastApi-Biblioteca/
├── main.py                     # Punto de entrada FastAPI, startup y seed inicial
├── dependencies.py             # Inyección de dependencias (SessionDep -> RepoDep -> ServiceDep)
├── api/                        # Capa de Presentación / Controladores HTTP
│   ├── payload/                # DTOs (Request y Response schemas de Pydantic)
│   ├── autor_controller.py     # Endpoints de /autores
│   ├── libro_controller.py     # Endpoints de /libros y asociación de autores
│   ├── socio_controller.py     # Endpoints de /socios y préstamos por socio
│   └── prestamo_controller.py  # Endpoints de /prestamos y devolución
├── services/                   # Capa de Lógica de Negocio (Interfaces + Implementaciones)
│   ├── autor_service.py
│   ├── libro_service.py
│   ├── socio_service.py
│   └── prestamo_service.py
├── repositories/               # Capa de Acceso a Datos (Consultas SQLModel y persistencia)
│   ├── database.py             # Configuración de SQLite engine y sesión
│   ├── autor_repository.py
│   ├── libro_repository.py
│   ├── socio_repository.py
│   └── prestamo_repository.py
├── models/                     # Modelos de Dominio y Tablas SQLModel
│   ├── autor.py
│   ├── libro.py
│   ├── libro_autor.py          # Tabla intermedia N:N (libros_autores)
│   ├── socio.py
│   └── prestamo.py
├── exceptions/                 # Jerarquía de Excepciones de Dominio (desacopladas de HTTP)
│   ├── autor_exceptions.py
│   ├── libro_exceptions.py
│   ├── socio_exceptions.py
│   └── prestamo_exceptions.py
└── tests/                      # Suite de pruebas automatizadas (167 tests, 98% cov)
    ├── conftest.py             # Fixtures, DB en memoria y TestClient
    ├── api/                    # Pruebas de integración HTTP
    ├── services/               # Pruebas unitarias de reglas de negocio
    └── repositories/           # Pruebas unitarias de persistencia
```

---

## 📌 Resumen de Endpoints Principales

| Método | Endpoint | Descripción | Requiere Rol |
| :--- | :--- | :--- | :--- |
| `GET` | `/autores` | Lista autores | Público |
| `POST` | `/autores` | Crea un nuevo autor | `bibliotecario` |
| `GET` / `PUT` / `PATCH` / `DELETE` | `/autores/{id}` | Operaciones sobre autor específico | `bibliotecario` (`GET` es público) |
| `GET` | `/libros` | Lista libros (soporta `?disponibles=true/false`) | Público |
| `POST` | `/libros` | Crea un nuevo libro | `bibliotecario` |
| `GET` / `PUT` / `PATCH` / `DELETE` | `/libros/{id}` | Operaciones sobre libro específico | `bibliotecario` (`GET` es público) |
| `POST` | `/libros/{id}/autores/{autor_id}` | Asocia un autor a un libro | `bibliotecario` |
| `GET` | `/socios` | Lista socios (soporta `?activos=true/false`) | `bibliotecario` |
| `POST` | `/socios` | Registra un nuevo socio | `bibliotecario` |
| `GET` / `PUT` / `PATCH` / `DELETE` | `/socios/{id}` | Operaciones sobre socio específico | `bibliotecario` |
| `GET` | `/socios/{id}/prestamos` | Préstamos de un socio (soporta `?activos=true/false`) | `bibliotecario` o propio `socio` |
| `GET` | `/prestamos` | Lista general de préstamos | `bibliotecario` o propio `socio` |
| `POST` | `/prestamos` | Registra préstamo (14 días, descuenta stock) | `bibliotecario` |
| `POST` | `/prestamos/{id}/devolucion` | Registra devolución, repone stock y liquida multa | `bibliotecario` |
