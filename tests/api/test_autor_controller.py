from fastapi.testclient import TestClient


# Obtener listado de autores (endpoint público)
def test_get_autores_ok(client: TestClient, seed: None) -> None:
    res = client.get("/autores")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 3
    assert any(a["nombre"] == "Jorge Luis Borges" for a in data)


# Obtener listado de autores con paginación
def test_get_autores_pagination(client: TestClient, seed: None) -> None:
    res = client.get("/autores?offset=1&limit=1")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["id"] == 2


# Obtener autor por ID existente
def test_get_autor_by_id_ok(client: TestClient, seed: None) -> None:
    res = client.get("/autores/1")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == 1
    assert data["nombre"] == "Jorge Luis Borges"
    assert "libros" in data


# Obtener autor por ID inexistente (404)
def test_get_autor_by_id_not_found(client: TestClient, seed: None) -> None:
    res = client.get("/autores/999")
    assert res.status_code == 404
    assert "999" in res.json()["detail"]


# Crear autor con datos válidos y rol bibliotecario (201)
def test_create_autor_ok(client: TestClient, bibliotecario_headers: dict[str, str]) -> None:
    payload = {"nombre": "Alfonsina Storni", "nacionalidad=" "Argentina": "Argentina"}
    payload = {"nombre": "Alfonsina Storni", "nacionalidad": "Argentina"}
    res = client.post("/autores", json=payload, headers=bibliotecario_headers)
    assert res.status_code == 201
    data = res.json()
    assert "id" in data
    assert data["nombre"] == "Alfonsina Storni"


# Crear autor rechazado por falta de permisos (403)
def test_create_autor_forbidden_socio(client: TestClient, socio_headers: dict[str, str]) -> None:
    payload = {"nombre": "Alfonsina Storni", "nacionalidad": "Argentina"}
    res = client.post("/autores", json=payload, headers=socio_headers)
    assert res.status_code == 403


# Crear autor rechazado sin cabeceras de rol (403)
def test_create_autor_forbidden_sin_rol(client: TestClient) -> None:
    payload = {"nombre": "Alfonsina Storni", "nacionalidad": "Argentina"}
    res = client.post("/autores", json=payload)
    assert res.status_code == 403


# Crear autor rechazado por validación de esquema Pydantic (422)
def test_create_autor_invalid_payload(client: TestClient, bibliotecario_headers: dict[str, str]) -> None:
    # nombre demasiado corto (< 3 caracteres)
    payload = {"nombre": "A", "nacionalidad": "Argentina"}
    res = client.post("/autores", json=payload, headers=bibliotecario_headers)
    assert res.status_code == 422


# Reemplazar completamente los datos de un autor (PUT 200)
def test_replace_autor_ok(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    payload = {"nombre": "Jorge Luis Borges (Modificado)", "nacionalidad": "Argentina"}
    res = client.put("/autores/1", json=payload, headers=bibliotecario_headers)
    assert res.status_code == 200
    assert res.json()["nombre"] == "Jorge Luis Borges (Modificado)"


# Reemplazar autor inexistente (PUT 404)
def test_replace_autor_not_found(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    payload = {"nombre": "Inexistente", "nacionalidad": "Desconocida"}
    res = client.put("/autores/999", json=payload, headers=bibliotecario_headers)
    assert res.status_code == 404


# Reemplazar autor rechazado por rol socio (PUT 403)
def test_replace_autor_forbidden(
    client: TestClient,
    socio_headers: dict[str, str],
    seed: None,
) -> None:
    payload = {"nombre": "Intento de Modificación", "nacionalidad": "Argentina"}
    res = client.put("/autores/1", json=payload, headers=socio_headers)
    assert res.status_code == 403


# Actualizar parcialmente un autor (PATCH 200)
def test_update_autor_patch_ok(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    payload = {"nacionalidad": "Rioplatense"}
    res = client.patch("/autores/1", json=payload, headers=bibliotecario_headers)
    assert res.status_code == 200
    assert res.json()["nacionalidad"] == "Rioplatense"
    assert res.json()["nombre"] == "Jorge Luis Borges"


# Actualizar parcialmente autor con valor nulo prohibido (PATCH 400)
def test_update_autor_patch_invalid_null(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    payload = {"nombre": None}
    res = client.patch("/autores/1", json=payload, headers=bibliotecario_headers)
    assert res.status_code == 400


# Actualizar parcialmente autor inexistente (PATCH 404)
def test_update_autor_patch_not_found(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    payload = {"nombre": "Nuevo Nombre"}
    res = client.patch("/autores/999", json=payload, headers=bibliotecario_headers)
    assert res.status_code == 404


# Eliminar un autor sin libros asociados (DELETE 204)
def test_delete_autor_ok(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
) -> None:
    create_res = client.post(
        "/autores",
        json={"nombre": "Autor Para Borrar", "nacionalidad": "Argentina"},
        headers=bibliotecario_headers,
    )
    autor_id = create_res.json()["id"]

    del_res = client.delete(f"/autores/{autor_id}", headers=bibliotecario_headers)
    assert del_res.status_code == 204

    # Verificar que ya no existe
    assert client.get(f"/autores/{autor_id}").status_code == 404


# Eliminar autor rechazado por tener libros asociados (DELETE 409)
def test_delete_autor_con_libros(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    res = client.delete("/autores/1", headers=bibliotecario_headers)
    assert res.status_code == 409


# Eliminar autor inexistente (DELETE 404)
def test_delete_autor_not_found(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    res = client.delete("/autores/999", headers=bibliotecario_headers)
    assert res.status_code == 404


# Eliminar autor rechazado por rol socio (DELETE 403)
def test_delete_autor_forbidden(
    client: TestClient,
    socio_headers: dict[str, str],
    seed: None,
) -> None:
    res = client.delete("/autores/1", headers=socio_headers)
    assert res.status_code == 403
