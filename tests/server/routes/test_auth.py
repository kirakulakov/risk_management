from sqlite3 import Cursor

from starlette.testclient import TestClient


def test_sign_up(client: TestClient, cursor: Cursor):
    response = client.post("/api/auth/sign-up", json={})
    assert response.status_code == 422

    count_account_db = cursor.execute(
        "SELECT COUNT(*) FROM accounts"
    )
    assert count_account_db.fetchone()[0] == 0

    payload = {
        "email": "1@1.com",
        "password": "1",
        "name": "1",
        "projectName": "1",
        "projectDescription": "1",
        "projectId": 1,
    }
    response = client.post("/api/auth/sign-up", json=payload)
    assert response.status_code != 200

    payload = {
        "email": "111@111.com",
        "password": "1",
        "name": "1",
        "projectName": "1",
        "projectDescription": "1",
        "projectId": 1,
    }
    response = client.post("/api/auth/sign-up", json=payload)
    assert response.status_code != 200

    payload = {
        "email": "111@111.com",
        "password": "123446",
        "name": "12345",
        "projectName": "Name",
        "projectDescription": "Desc",
        "projectId": "TTD",
    }

    response = client.post("/api/auth/sign-up", json=payload)
    assert response.status_code == 200

    token = response.json().get("access_token")
    assert token is not None

    payload = {
        "email": "222@222.com",
        "password": "123446",
        "name": "12345",
        "projectName": "Name",
        "projectDescription": "Desc",
        "projectId": "TTD",
    }

    response = client.post("/api/auth/sign-up", json=payload)
    assert response.status_code == 200

    count_account_db = cursor.execute(
        "SELECT COUNT(*) FROM accounts"
    )
    assert count_account_db.fetchone()[0] == 2
