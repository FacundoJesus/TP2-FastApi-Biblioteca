from fastapi.testclient import TestClient


# Obtener listado de todos los préstamos como bibliotecario (200)
def test_get_prestamos_as_bibliotecario(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    res = client.get("/prestamos", headers=bibliotecario_headers)
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 3


# Obtener solo los préstamos propios al consultar como socio (200)
def test_get_prestamos_as_socio(
    client: TestClient,
    socio_headers: dict[str, str],
    seed: None,
) -> None:
    # Socio 1 tiene 2 préstamos registrados en el seed
    res = client.get("/prestamos", headers=socio_headers)
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2
    assert all(p["socio_id"] == 1 for p in data)


# Consulta de préstamos como socio rechazada sin cabecera X-Socio-Id (400)
def test_get_prestamos_as_socio_missing_header(client: TestClient, seed: None) -> None:
    # Sin headers asume rol 'socio' por defecto
    res = client.get("/prestamos")
    assert res.status_code == 400
    assert "X-Socio-Id" in res.json()["detail"]


# Consulta de préstamos como socio con ID inexistente (404)
def test_get_prestamos_as_socio_inexistente(client: TestClient, seed: None) -> None:
    res = client.get("/prestamos", headers={"X-Rol": "socio", "X-Socio-Id": "999"})
    assert res.status_code == 404


# Obtener préstamo por ID como bibliotecario (200)
def test_get_prestamo_by_id_as_bibliotecario(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    res = client.get("/prestamos/1", headers=bibliotecario_headers)
    assert res.status_code == 200
    assert res.json()["id"] == 1
    assert "libro" in res.json()


# Obtener préstamo propio como socio (200)
def test_get_prestamo_by_id_own_socio(
    client: TestClient,
    socio_headers: dict[str, str],
    seed: None,
) -> None:
    # Socio 1 consulta el préstamo 1 (que le pertenece)
    res = client.get("/prestamos/1", headers=socio_headers)
    assert res.status_code == 200
    assert res.json()["id"] == 1


# Consulta de préstamo ajeno rechazada con rol socio (403)
def test_get_prestamo_by_id_other_socio_forbidden(
    client: TestClient,
    socio2_headers: dict[str, str],
    seed: None,
) -> None:
    # Socio 2 intenta consultar el préstamo 1 (perteneciente a Socio 1)
    res = client.get("/prestamos/1", headers=socio2_headers)
    assert res.status_code == 403
    assert "solo puede consultar sus propios préstamos" in res.json()["detail"]


# Obtener préstamo por ID inexistente (404)
def test_get_prestamo_by_id_not_found(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    res = client.get("/prestamos/999", headers=bibliotecario_headers)
    assert res.status_code == 404


# Registrar un nuevo préstamo con rol bibliotecario (201)
def test_create_prestamo_ok(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    payload = {"socio_id": 1, "libro_id": 2}
    res = client.post("/prestamos", json=payload, headers=bibliotecario_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["socio_id"] == 1
    assert data["libro_id"] == 2
    assert data["fecha_devolucion"] is None


# Registro de préstamo rechazado con rol socio (403)
def test_create_prestamo_forbidden_as_socio(
    client: TestClient,
    socio_headers: dict[str, str],
    seed: None,
) -> None:
    payload = {"socio_id": 1, "libro_id": 2}
    res = client.post("/prestamos", json=payload, headers=socio_headers)
    assert res.status_code == 403


# Registro de préstamo con socio inexistente (404)
def test_create_prestamo_socio_inexistente(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    payload = {"socio_id": 999, "libro_id": 1}
    res = client.post("/prestamos", json=payload, headers=bibliotecario_headers)
    assert res.status_code == 404


# Registro de préstamo con libro inexistente (404)
def test_create_prestamo_libro_inexistente(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    payload = {"socio_id": 1, "libro_id": 999}
    res = client.post("/prestamos", json=payload, headers=bibliotecario_headers)
    assert res.status_code == 404


# Registro de préstamo con socio inactivo rechazado (403)
def test_create_prestamo_socio_inactivo(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    # Socio 3 está inactivo
    payload = {"socio_id": 3, "libro_id": 1}
    res = client.post("/prestamos", json=payload, headers=bibliotecario_headers)
    assert res.status_code == 403
    assert "inactivo" in res.json()["detail"].lower()


# Registro de préstamo rechazado cuando el socio alcanza el límite de préstamos activos (409)
def test_create_prestamo_socio_limite_alcanzado(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    # Socio 1 ya tiene 1 préstamo activo. Creamos 2 más para alcanzar el máximo de 3:
    client.post("/prestamos", json={"socio_id": 1, "libro_id": 1}, headers=bibliotecario_headers)
    client.post("/prestamos", json={"socio_id": 1, "libro_id": 1}, headers=bibliotecario_headers)

    # Intentar el 4to préstamo activo
    res = client.post("/prestamos", json={"socio_id": 1, "libro_id": 1}, headers=bibliotecario_headers)
    assert res.status_code == 409
    assert "límite" in res.json()["detail"] or "limite" in res.json()["detail"]


# Registro de préstamo rechazado por falta de stock (409)
def test_create_prestamo_libro_sin_stock(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    # Agotar stock del libro 2 (stock = 3)
    client.patch("/libros/2", json={"stock": 0}, headers=bibliotecario_headers)

    payload = {"socio_id": 1, "libro_id": 2}
    res = client.post("/prestamos", json=payload, headers=bibliotecario_headers)
    assert res.status_code == 409
    assert "stock" in res.json()["detail"].lower()


# Registro de préstamo rechazado por payload inválido (422)
def test_create_prestamo_invalid_payload(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    # IDs no positivos
    payload = {"socio_id": -1, "libro_id": 0}
    res = client.post("/prestamos", json=payload, headers=bibliotecario_headers)
    assert res.status_code == 422


# Registrar devolución a término sin multa (200)
def test_registrar_devolucion_ok_sin_multa(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    res = client.post("/prestamos/1/devolucion", headers=bibliotecario_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == 1
    assert data["fecha_devolucion"] is not None
    assert data["multa"] == 0.0


# Registrar devolución con atraso y multa calculada (200)
def test_registrar_devolucion_con_multa(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    # Préstamo 3 venció hace 1 día en el seed ($100 x 1 día = 100.0)
    res = client.post("/prestamos/3/devolucion", headers=bibliotecario_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == 3
    assert data["multa"] == 100.0


# Registrar devolución de préstamo ya devuelto (409)
def test_registrar_devolucion_ya_devuelto(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    # Préstamo 2 ya fue devuelto en el seed
    res = client.post("/prestamos/2/devolucion", headers=bibliotecario_headers)
    assert res.status_code == 409


# Registrar devolución de préstamo inexistente (404)
def test_registrar_devolucion_not_found(
    client: TestClient,
    bibliotecario_headers: dict[str, str],
    seed: None,
) -> None:
    res = client.post("/prestamos/999/devolucion", headers=bibliotecario_headers)
    assert res.status_code == 404


# Registrar devolución rechazada por rol socio (403)
def test_registrar_devolucion_forbidden_as_socio(
    client: TestClient,
    socio_headers: dict[str, str],
    seed: None,
) -> None:
    res = client.post("/prestamos/1/devolucion", headers=socio_headers)
    assert res.status_code == 403
