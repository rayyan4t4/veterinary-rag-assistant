from tests.conftest import auth
from ai.safety.triage import assess_triage


async def test_health(client):
    assert (await client.get("/health")).json()["status"] == "ok"


async def test_auth_required(client):
    assert (await client.get("/api/v1/animals")).status_code == 401


async def test_animal_crud_and_cross_user_isolation(client):
    payload = {"name": "Milo", "species": "cat", "weight": 4.2}
    created = await client.post("/api/v1/animals", json=payload, headers=auth())
    assert created.status_code == 201
    animal_id = created.json()["id"]
    assert (await client.get(f"/api/v1/animals/{animal_id}", headers=auth())).status_code == 200
    assert (await client.get(f"/api/v1/animals/{animal_id}", headers=auth("user-b"))).status_code == 404


def test_emergency_triage():
    result = assess_triage("My dog collapsed and is not responding")
    assert result.urgency == "emergency"
    assert result.red_flags


def test_non_emergency_triage():
    assert assess_triage("My cat scratched its ear once").urgency == "monitor"


async def test_insufficient_evidence_is_explicit(client):
    result = await client.post("/api/v1/chat", json={"text": "Why is my dog limping?", "species": "dog"}, headers=auth())
    assert "not have enough reliable information" in result.json()["answer"]
    assert result.json()["citations"] == []
