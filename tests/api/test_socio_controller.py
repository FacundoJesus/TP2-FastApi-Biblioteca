from fastapi.testclient import TestClient


# Obtener listado de socios (público)
def test_get_socios_ok(client: TestClient, seed: None) -> None:
    res = client.get("/socios")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 3
    assert any(s["nombre"] == "Juan Pérez" for s in data)


# Filtrar socios por estado activo (activos=true y activos=false)
def test_get_socios_filter_activos(client: TestClient, seed: None) -> None:
    res_activos = client.get("/socios?activos=true")
    assert res_activos.status_code == 200
    assert len(res_activos.json()) == 2

    res_inactivos = client.get("/socios?activos=false")
    assert res_inactivos.status_code == 200
    assert len(res_inactivos.json()) == 1
    assert res_inactivos.json()[0]["id"] == 3


# Obtener socio por ID existente
def test_get_socio_by_id_ok(client: TestClient, seed: None) -> None:
    res = client.get("/socios/1")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == 1
    assert data["email"] == "juan.perez@utn.edu.ar"


# Obtener socio por ID inexistente (404)
def test_get_socio_by_id_not_found(client: TestClient, seed: None) -> None:
    res = client.get("/socios/999")
    assert res.status_code == 404
    assert "999" in res.json()["detail"]


# Obtener préstamos de un socio como bibliotecario (200)
def test_get_prestamos_socio_as_bibliotecario(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    res = client.get("/socios/1/prestamos", headers=bibliotecario_headers)
    assert res.status_code == 200
    assert len(res.json()) == 2


# Obtener préstamos propios como socio con cabecera X-Socio-Id (200)
def test_get_prestamos_socio_own(
    client: TestClient,
    socio_headers: dict[str, str],
    seed: None,
) -> None:
    # Socio 1 consulta sus propios préstamos
    res = client.get("/socios/1/prestamos", headers=socio_headers)
    assert res.status_code == 200
    assert len(res.json()) == 2


# Consulta de préstamos ajenos rechazada con rol socio (403)
def test_get_prestamos_socio_forbidden_other(
    client: TestClient,
    socio_headers: dict[str, str],
    seed: None,
) -> None:
    # Socio 1 intenta consultar préstamos de Socio 2
    res = client.get("/socios/2/prestamos", headers=socio_headers)
    assert res.status_code == 403
    assert "solo puede consultar sus propios préstamos" in res.json()["detail"]


# Consulta de préstamos como socio sin cabecera X-Socio-Id (400)
def test_get_prestamos_socio_missing_header(client: TestClient, seed: None) -> None:
    # Sin cabeceras asume rol 'socio' pero no envía X-Socio-Id
    res = client.get("/socios/1/prestamos")
    assert res.status_code == 400
    assert "X-Socio-Id" in res.json()["detail"]


# Obtener préstamos de socio inexistente (404)
def test_get_prestamos_socio_not_found(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    res = client.get("/socios/999/prestamos", headers=bibliotecario_headers)
    assert res.status_code == 404


# Filtrar préstamos de socio por estado activo (activos=true)
def test_get_prestamos_socio_filter_activos(
    client: TestClient,
    socio_headers: dict[str, str],
    seed: None,
) -> None:
    res = client.get("/socios/1/prestamos?activos=true", headers=socio_headers)
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["fecha_devolucion"] is None


# Crear un nuevo socio con rol bibliotecario (201)
def test_create_socio_ok(client: TestClient, bibliotecario_headers: dict[str, str]) -> None:
    payload = {
        "nombre": "Ana Frank",
        "email": "ana.frank@utn.edu.ar",
        "activo": True,
    }
    res = client.post("/socios", json=payload, headers=bibliotecario_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["nombre"] == "Ana Frank"
    assert data["email"] == "ana.frank@utn.edu.ar"


# Crear socio rechazado por email duplicado (409)
def test_create_socio_email_duplicado(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    payload = {
        "nombre": "Otro Juan",
        "email": "juan.perez@utn.edu.ar",
        "activo": True,
    }
    res = client.post("/socios", json=payload, headers=bibliotecario_headers)
    assert res.status_code == 409


# Crear socio rechazado por rol socio (403)
def test_create_socio_forbidden(client: TestClient, socio_headers: dict[str, str]) -> None:
    payload = {
        "nombre": "Intruso",
        "email": "intruso@utn.edu.ar",
        "activo": True,
    }
    res = client.post("/socios", json=payload, headers=socio_headers)
    assert res.status_code == 403


# Crear socio rechazado por formato de email inválido (422)
def test_create_socio_invalid_email(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
) -> None:
    payload = {
        "nombre": "Email Invalido",
        "email": "no-es-un-email",
        "activo": True,
    }
    res = client.post("/socios", json=payload, headers=bibliotecario_headers)
    assert res.status_code == 422


# Reemplazar completamente un socio (PUT 200)
def test_replace_socio_ok(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    payload = {
        "nombre": "Juan Carlos Pérez",
        "email": "juan.perez@utn.edu.ar",
        "activo": False,
    }
    res = client.put("/socios/1", json=payload, headers=bibliotecario_headers)
    assert res.status_code == 200
    assert res.json()["nombre"] == "Juan Carlos Pérez"
    assert not res.json()["activo"]


# Reemplazar socio con email de otro socio (PUT 409)
def test_replace_socio_email_duplicado(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    # Intentar asignar al socio 1 el email de la socia 2
    payload = {
        "nombre": "Conflicto",
        "email": "maria.lopez@utn.edu.ar",
        "activo": True,
    }
    res = client.put("/socios/1", json=payload, headers=bibliotecario_headers)
    assert res.status_code == 409


# Reemplazar socio inexistente (PUT 404)
def test_replace_socio_not_found(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    payload = {
        "nombre": "Inexistente",
        "email": "inexistente@utn.edu.ar",
        "activo": True,
    }
    res = client.put("/socios/999", json=payload, headers=bibliotecario_headers)
    assert res.status_code == 404


# Actualizar parcialmente un socio (PATCH 200)
def test_update_socio_patch_ok(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    payload = {"activo": False}
    res = client.patch("/socios/1", json=payload, headers=bibliotecario_headers)
    assert res.status_code == 200
    assert not res.json()["activo"]


# Actualizar parcialmente socio con campo nulo prohibido (PATCH 400)
def test_update_socio_patch_invalid_null(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    payload = {"nombre": None}
    res = client.patch("/socios/1", json=payload, headers=bibliotecario_headers)
    assert res.status_code == 400


# Actualizar parcialmente socio inexistente (PATCH 404)
def test_update_socio_patch_not_found(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    payload = {"nombre": "Nuevo Nombre"}
    res = client.patch("/socios/999", json=payload, headers=bibliotecario_headers)
    assert res.status_code == 404


# Eliminar socio sin préstamos asociados (DELETE 204)
def test_delete_socio_ok(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    # Socio 3 no tiene préstamos registrados
    res = client.delete("/socios/3", headers=bibliotecario_headers)
    assert res.status_code == 204
    assert client.get("/socios/3").status_code == 404


# Eliminar socio rechazado por registrar préstamos (DELETE 409)
def test_delete_socio_con_prestamos(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    # Socio 1 tiene préstamos asociados
    res = client.delete("/socios/1", headers=bibliotecario_headers)
    assert res.status_code == 409


# Eliminar socio inexistente (DELETE 404)
def test_delete_socio_not_found(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    res = client.delete("/socios/999", headers=bibliotecario_headers)
    assert res.status_code == 404


# Eliminar socio rechazado por rol socio (DELETE 403)
def test_delete_socio_forbidden(
    client: TestClient,
    socio_headers: dict[str, str],
    seed: None,
) -> None:
    res = client.delete("/socios/3", headers=socio_headers)
    assert res.status_code == 403
