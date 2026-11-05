from fastapi.testclient import TestClient


# Obtener listado general de libros (público)
def test_get_libros_ok(client: TestClient, seed: None) -> None:
    res = client.get("/libros")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 3
    assert any(l["titulo"] == "El Aleph" for l in data)


# Obtener listado de libros con paginación
def test_get_libros_pagination(client: TestClient, seed: None) -> None:
    res = client.get("/libros?offset=1&limit=1")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["id"] == 2


# Filtrar libros por disponibilidad de stock (disponibles=true)
def test_get_libros_filter_disponibles(client: TestClient, seed: None) -> None:
    res = client.get("/libros?disponibles=true")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 3
    assert all(l["stock"] > 0 for l in data)


# Obtener libro por ID existente
def test_get_libro_by_id_ok(client: TestClient, seed: None) -> None:
    res = client.get("/libros/1")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == 1
    assert data["titulo"] == "El Aleph"
    assert "autores" in data
    assert len(data["autores"]) >= 1


# Obtener libro por ID inexistente (404)
def test_get_libro_by_id_not_found(client: TestClient, seed: None) -> None:
    res = client.get("/libros/999")
    assert res.status_code == 404
    assert "999" in res.json()["detail"]


# Crear libro con rol bibliotecario (201)
def test_create_libro_ok(client: TestClient, bibliotecario_headers: dict[str, str]) -> None:
    payload = {
        "titulo": "Ficciones",
        "anio": 1944,
        "isbn": "978-950-07-0000-1",
        "stock": 5,
    }
    res = client.post("/libros", json=payload, headers=bibliotecario_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["titulo"] == "Ficciones"
    assert data["isbn"] == "978-950-07-0000-1"


# Crear libro rechazado por ISBN duplicado (409)
def test_create_libro_isbn_duplicado(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    payload = {
        "titulo": "Otro Titulo",
        "isbn": "978-950-07-2575-0",  # ISBN ya registrado
        "stock": 1,
    }
    res = client.post("/libros", json=payload, headers=bibliotecario_headers)
    assert res.status_code == 409


# Crear libro rechazado por rol socio (403)
def test_create_libro_forbidden_socio(client: TestClient, socio_headers: dict[str, str]) -> None:
    payload = {
        "titulo": "Libro Prohibido",
        "isbn": "978-950-07-0000-2",
        "stock": 2,
    }
    res = client.post("/libros", json=payload, headers=socio_headers)
    assert res.status_code == 403


# Crear libro rechazado por esquema inválido (422)
def test_create_libro_invalid_payload(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
) -> None:
    # stock negativo
    payload = {
        "titulo": "Libro Invalido",
        "isbn": "978-950-07-0000-3",
        "stock": -1,
    }
    res = client.post("/libros", json=payload, headers=bibliotecario_headers)
    assert res.status_code == 422


# Asociar un autor existente a un libro existente (POST 200)
def test_asociar_autor_a_libro_ok(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    # Asociar Autor 2 a Libro 1
    res = client.post("/libros/1/autores/2", headers=bibliotecario_headers)
    assert res.status_code == 200
    data = res.json()
    assert any(a["id"] == 2 for a in data["autores"])


# Asociar autor a libro inexistente (404)
def test_asociar_autor_a_libro_libro_inexistente(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    res = client.post("/libros/999/autores/1", headers=bibliotecario_headers)
    assert res.status_code == 404


# Asociar autor inexistente a libro existente (404)
def test_asociar_autor_a_libro_autor_inexistente(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    res = client.post("/libros/1/autores/999", headers=bibliotecario_headers)
    assert res.status_code == 404


# Asociar autor ya asociado a un libro (409)
def test_asociar_autor_a_libro_ya_asociado(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    # Autor 1 ya está asociado a Libro 1 en el seed
    res = client.post("/libros/1/autores/1", headers=bibliotecario_headers)
    assert res.status_code == 409


# Asociar autor rechazado por rol socio (403)
def test_asociar_autor_a_libro_forbidden(
    client: TestClient,
    socio_headers: dict[str, str],
    seed: None,
) -> None:
    res = client.post("/libros/1/autores/2", headers=socio_headers)
    assert res.status_code == 403


# Reemplazar completamente un libro (PUT 200)
def test_replace_libro_ok(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    payload = {
        "titulo": "El Aleph (Edición Definitiva)",
        "anio": 1952,
        "isbn": "978-950-07-2575-0",
        "stock": 10,
    }
    res = client.put("/libros/1", json=payload, headers=bibliotecario_headers)
    assert res.status_code == 200
    assert res.json()["titulo"] == "El Aleph (Edición Definitiva)"
    assert res.json()["stock"] == 10


# Reemplazar libro inexistente (PUT 404)
def test_replace_libro_not_found(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    payload = {
        "titulo": "Inexistente",
        "isbn": "978-950-07-9999-9",
        "stock": 1,
    }
    res = client.put("/libros/999", json=payload, headers=bibliotecario_headers)
    assert res.status_code == 404


# Reemplazar libro con conflicto de ISBN duplicado (PUT 409)
def test_replace_libro_isbn_duplicado(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    # Intentar asignar al libro 1 el ISBN del libro 2
    payload = {
        "titulo": "Conflicto",
        "isbn": "978-84-376-0494-7",
        "stock": 2,
    }
    res = client.put("/libros/1", json=payload, headers=bibliotecario_headers)
    assert res.status_code == 409


# Actualizar parcialmente un libro (PATCH 200)
def test_update_libro_patch_ok(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    payload = {"stock": 25}
    res = client.patch("/libros/1", json=payload, headers=bibliotecario_headers)
    assert res.status_code == 200
    assert res.json()["stock"] == 25
    assert res.json()["titulo"] == "El Aleph"


# Actualizar parcialmente libro con campo nulo prohibido (PATCH 400)
def test_update_libro_patch_invalid_null(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    payload = {"stock": None}
    res = client.patch("/libros/1", json=payload, headers=bibliotecario_headers)
    assert res.status_code == 400


# Actualizar parcialmente libro inexistente (PATCH 404)
def test_update_libro_patch_not_found(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    payload = {"stock": 10}
    res = client.patch("/libros/999", json=payload, headers=bibliotecario_headers)
    assert res.status_code == 404


# Eliminar un libro sin préstamos asociados (DELETE 204)
def test_delete_libro_ok(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
) -> None:
    create_res = client.post(
        "/libros",
        json={
            "titulo": "Libro Efimero",
            "isbn": "978-950-07-7777-7",
            "stock": 2,
        },
        headers=bibliotecario_headers,
    )
    libro_id = create_res.json()["id"]

    del_res = client.delete(f"/libros/{libro_id}", headers=bibliotecario_headers)
    assert del_res.status_code == 204
    assert client.get(f"/libros/{libro_id}").status_code == 404


# Eliminar libro rechazado por registrar préstamos (DELETE 409)
def test_delete_libro_con_prestamos(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    # Libro 1 tiene préstamos asociados
    res = client.delete("/libros/1", headers=bibliotecario_headers)
    assert res.status_code == 409


# Eliminar libro inexistente (DELETE 404)
def test_delete_libro_not_found(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    res = client.delete("/libros/999", headers=bibliotecario_headers)
    assert res.status_code == 404


# Eliminar libro rechazado por rol socio (DELETE 403)
def test_delete_libro_forbidden(
    client: TestClient,
    socio_headers: dict[str, str],
    seed: None,
) -> None:
    res = client.delete("/libros/1", headers=socio_headers)
    assert res.status_code == 403
