from sqlite3 import Cursor, Connection

from starlette.testclient import TestClient


def test_types(client: TestClient):
    response = client.get(f"/api/risks/types")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_statuses(client: TestClient):
    response = client.get(f"/api/risks/statuses")
    assert response.status_code == 200
    assert len(response.json()) == 3

def test_probabilities(client: TestClient):
    response = client.get(f"/api/risks/probabilities")
    assert response.status_code == 200
    assert len(response.json()) == 5

def test_impacts(client: TestClient):
    response = client.get(f"/api/risks/impacts")
    assert response.status_code == 200
    assert len(response.json()) == 5


def test_factors(client: TestClient):
    response = client.get(f"/api/risks/factors")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_methods(client: TestClient):
    response = client.get(f"/api/risks/management-methods")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_risks(client: TestClient, cursor: Cursor, connection: Connection):
    ids = list()
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
    ids.append(new_id)


    payload = {
        "id": new_id,
        "name": "string1",
        "description": "string1",
        "comment": "string1",
        "factor_id": 1,
        "type_id": 1,
        "method_id": 1,
        "probability_id": 1,
        "impact_id": 1,

    }
    response = client.post(f"/api/risks", headers=auth, json=payload)
    assert response.status_code == 200
    assert response.json()['name'] == payload['name']
    assert response.json()['description'] == payload['description']
    assert response.json()['comment'] == payload['comment']
    assert response.json()['factor']['id'] == payload['factor_id']
    assert response.json()['type']['id'] == payload['type_id']
    assert response.json()['method']['id'] == payload['method_id']
    assert response.json()['probability']['id'] == payload['probability_id']
    assert response.json()['impact']['id'] == payload['impact_id']
    assert response.json()['status']['id'] == 1


    response = client.get(f"/api/risks/new-id", headers=auth)
    assert response.status_code == 200
    new_id = response.json()
    assert new_id is not None
    ids.append(new_id)

    payload = {
        "id": new_id,
        "name": "string1",
        "description": "string1",
        "comment": "string1",
        "factor_id": 1,
        "type_id": 1,
        "method_id": 1,
        "probability_id": 3,
        "impact_id": 3
    }
    response = client.post(f"/api/risks", headers=auth, json=payload)
    assert response.status_code == 200


    count_risk_db = cursor.execute(
        "SELECT COUNT(*) FROM risks"
    )
    assert count_risk_db.fetchone()[0] == 2

    response = client.get(f"/api/risks", headers=auth)
    assert response.status_code == 200
    assert len(response.json()) == 2
    for r in response.json():
        assert r['id'] in ids

    response = client.delete(f"/api/risks/{new_id}", headers=auth)
    assert response.status_code == 200

    count_risk_db = cursor.execute(
        "SELECT COUNT(*) FROM risks"
    )
    assert count_risk_db.fetchone()[0] == 1

    response = client.get(f"/api/risks", headers=auth)
    assert response.status_code == 200
    for r in response.json():
        assert r['description'] == 'string1'

    payload = {
        "id": new_id,
        "name": "string1",
        "factor_id": 1,
        "type_id": 1,
        "method_id": 1,
        "probability_id": 5,
        "impact_id": 5
    }
    response = client.post(f"/api/risks", headers=auth, json=payload)
    assert response.status_code == 200

    response = client.get(f"/api/risks", headers=auth)
    assert response.status_code == 200
    description_set = set()
    comment_set = set()

    for r in response.json():
        description_set.add(r['description'])
        comment_set.add(r['comment'])

    assert None in description_set
    assert 'string1' in description_set
    assert None in comment_set
    assert 'string1' in comment_set

    # update
    risk_id = response.json()[0]['id']
    risk_id_2 = response.json()[1]['id']
    payload = {
        "id": risk_id,
        "name": "string2",
        "description": "string2",
        "comment": "string2",
        "factor_id": 2,
        "type_id": 2,
        "method_id": 2,
        "probability_id": 2,
        "impact_id": 1,
        "status_id": 3
    }

    response = client.patch(f"/api/risks", headers=auth, json=payload)
    assert response.status_code == 200
    assert response.json()['name'] == payload['name']
    assert response.json()['description'] == payload['description']
    assert response.json()['comment'] == payload['comment']
    assert response.json()['factor']['id'] == payload['factor_id']
    assert response.json()['type']['id'] == payload['type_id']
    assert response.json()['method']['id'] == payload['method_id']
    assert response.json()['probability']['id'] == payload['probability_id']
    assert response.json()['impact']['id'] == payload['impact_id']
    assert response.json()['status']['id'] == payload['status_id']

    payload = {
        "id": risk_id,
        "name": "asasa"
    }

    response = client.patch(f"/api/risks", headers=auth, json=payload)
    assert response.status_code == 200
    assert response.json()['name'] == payload['name']

    payload = {
        "id": risk_id,
        "description": "qweqweqw"
    }

    response = client.patch(f"/api/risks", headers=auth, json=payload)
    assert response.status_code == 200
    assert response.json()['description'] == payload['description']

    payload = {
        "id": risk_id,
        "comment": "comme123nt"
    }

    response = client.patch(f"/api/risks", headers=auth, json=payload)
    assert response.status_code == 200
    assert response.json()['comment'] == payload['comment']

    payload = {
        "id": risk_id,
        "factor_id": 1,
        "type_id": 1,
        "method_id": 1
    }

    response = client.patch(f"/api/risks", headers=auth, json=payload)
    assert response.status_code == 200
    assert response.json()['factor']['id'] == payload['factor_id']
    assert response.json()['type']['id'] == payload['type_id']
    assert response.json()['method']['id'] == payload['method_id']
    assert response.json()['name'] == 'asasa'
    assert response.json()['description'] == 'qweqweqw'
    assert response.json()['comment'] == 'comme123nt'

    payload = {
        "id": risk_id,
        "factor_id": 2,
        "type_id": 2,
        "method_id": 2,
        "probability_id": 2,
        "impact_id": 2,
        "comment": "nice comment",
        "name": "nice name!!!"
    }

    response = client.patch(f"/api/risks", headers=auth, json=payload)
    assert response.status_code == 200

    payload = {
        "id": risk_id_2,
        "factor_id": 2,
        "type_id": 2,
        "method_id": 2,
        "probability_id": 2,
        "impact_id": 2,
        "comment": "nice comment AHAAHhahahha",
        "name": "nice name AHAHAHHA",
        "description": "nice description AHAHAHHA"
    }

    response = client.patch(f"/api/risks", headers=auth, json=payload)
    assert response.status_code == 200

    payload = {
        "id": risk_id_2,
        "factor_id": 1,
        "type_id": 1,
        "method_id": 1,
        "probability_id": 1,
        "impact_id": 1,
        "comment": "nice comment AHAAHhahahha2321321233",
        "name": "nice name AHAHAHHA2313123232",
        "description": "nice description AHAHAHHA3231232131223"
    }

    response = client.patch(f"/api/risks", headers=auth, json=payload)
    assert response.status_code == 200

    payload = {
        "id": 'HAAABB',
        "comment": "comme123nt"
    }

    response = client.patch(f"/api/risks", headers=auth, json=payload)
    assert response.status_code == 404
