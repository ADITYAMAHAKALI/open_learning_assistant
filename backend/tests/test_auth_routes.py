def test_signup_and_login_flow(client):
    # signup
    resp = client.post(
        "/api/v1/auth/signup",
        json={"email": "user1@example.com", "password": "pwd123", "name": "User One"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data

    # login
    resp_login = client.post(
        "/api/v1/auth/login",
        data={"username": "user1@example.com", "password": "pwd123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp_login.status_code == 200
    data_login = resp_login.json()
    assert "access_token" in data_login
    assert "refresh_token" in data_login


def test_refresh_and_logout(client):
    resp = client.post(
        "/api/v1/auth/signup",
        json={"email": "user2@example.com", "password": "pwd123"},
    )
    assert resp.status_code == 200
    tokens = resp.json()
    refresh = tokens["refresh_token"]

    # refresh
    resp_ref = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh},
    )
    assert resp_ref.status_code == 200
    new_tokens = resp_ref.json()
    assert new_tokens["access_token"] != tokens["access_token"]
    assert new_tokens["refresh_token"] != refresh

    # logout
    resp_logout = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": new_tokens["refresh_token"]},
    )
    assert resp_logout.status_code == 204
