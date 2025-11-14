import pytest


def _signup_and_get_token(client):
    resp = client.post(
        "/api/v1/auth/signup",
        json={"email": "learner@example.com", "password": "pwd123"},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


def _upload_material(client, token, filename):
    files = {
        "file": (filename, b"content", "application/pdf"),
    }
    resp = client.post(
        "/api/v1/materials/upload",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    assert resp.status_code == 201
    return resp.json()["material_id"]


@pytest.mark.usefixtures("client")
def test_create_and_fetch_learning_session(client):
    token = _signup_and_get_token(client)
    material_a = _upload_material(client, token, "lesson-a.pdf")
    material_b = _upload_material(client, token, "lesson-b.pdf")

    resp_create = client.post(
        "/api/v1/learning/sessions",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Exam Prep",
            "objective": "Understand the core topics",
            "material_ids": [material_a, material_b],
        },
    )
    assert resp_create.status_code == 201, resp_create.text
    session_id = resp_create.json()["id"]
    assert len(resp_create.json()["materials"]) == 2

    resp_list = client.get(
        "/api/v1/learning/sessions",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_list.status_code == 200
    assert len(resp_list.json()) == 1

    resp_detail = client.get(
        f"/api/v1/learning/sessions/{session_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_detail.status_code == 200
    assert resp_detail.json()["id"] == session_id
