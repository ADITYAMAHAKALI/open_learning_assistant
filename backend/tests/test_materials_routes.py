def _signup_and_get_token(client):
    resp = client.post(
        "/api/v1/auth/signup",
        json={"email": "matuser@example.com", "password": "pwd123"},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_list_materials_requires_auth(client):
    resp = client.get("/api/v1/materials/")
    assert resp.status_code == 401


def test_upload_and_list_materials(client):
    token = _signup_and_get_token(client)

    files = {
        "file": ("test.pdf", b"dummy content", "application/pdf"),
    }
    resp_upload = client.post(
        "/api/v1/materials/upload",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    assert resp_upload.status_code == 201, resp_upload.text
    material_id = resp_upload.json()["material_id"]
    assert material_id is not None

    resp_list = client.get(
        "/api/v1/materials/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_list.status_code == 200
    items = resp_list.json()
    assert len(items) == 1
    assert items[0]["id"] == material_id
