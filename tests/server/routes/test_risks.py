from sqlite3 import Cursor, Connection

from starlette.testclient import TestClient


def test_types(client: TestClient):
    response = client.get(f"/api/risks/types")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_factors(client: TestClient):
    response = client.get(f"/api/risks/factors")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_methods(client: TestClient):
    response = client.get(f"/api/risks/management-methods")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_risks(client: TestClient, cursor: Cursor, connection: Connection):
    cursor.execute("DELETE FROM accounts;")
    connection.commit()

    count_risk_db = cursor.execute(
        "SELECT COUNT(*) FROM risks"
    )
    assert count_risk_db.fetchone()[0] == 0

    payload = {
        "email": "somename@111.com",
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
    auth = {"Authorization": f"Bearer {token}"}

    response = client.get(f"/api/risks", headers=auth)
    assert response.status_code == 200
    assert len(response.json()) == 0

    response = client.get(f"/api/risks/new-id", headers=auth)
    assert response.status_code == 200
    new_id = response.json()
    assert new_id is not None

    payload = {
        "id": new_id,
        "name": "string1",
        "description": "string1",
        "comment": "string1",
        "factor_id": 1,
        "type_id": 1,
        "method_id": 1,
        "probability": 5,
        "impact": 5


    }
    response = client.post(f"/api/risks", headers=auth, json=payload)
    assert response.status_code == 200

    response = client.get(f"/api/risks/new-id", headers=auth)
    assert response.status_code == 200
    new_id = response.json()
    assert new_id is not None

    payload = {
        "id": new_id,
        "name": "string1",
        "description": "string1",
        "comment": "string1",
        "factor_id": 1,
        "type_id": 1,
        "method_id": 1,
        "probability": 5,
        "impact": 5


    }
    response = client.post(f"/api/risks", headers=auth, json=payload)
    assert response.status_code == 200

    count_risk_db = cursor.execute(
        "SELECT COUNT(*) FROM risks"
    )
    assert count_risk_db.fetchone()[0] == 2

    response = client.delete(f"/api/risks/{new_id}", headers=auth)
    assert response.status_code == 200

    count_risk_db = cursor.execute(
        "SELECT COUNT(*) FROM risks"
    )
    assert count_risk_db.fetchone()[0] == 1



