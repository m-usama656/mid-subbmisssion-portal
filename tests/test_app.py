import pytest

from app import create_app

VALID = {
    "name": "Ali Khan",
    "reg_no": "FA23-BSE-053",
    "title": "Lab 1",
    "url": "https://github.com/ali/lab1",
}


@pytest.fixture
def client(tmp_path):
    app = create_app(str(tmp_path / "submissions.json"))
    app.config["TESTING"] = True
    return app.test_client()


def test_valid_submission_is_saved_and_listed(client):
    r = client.post("/submit", data=VALID, follow_redirects=True)
    assert r.status_code == 200
    assert b"Ali Khan" in r.data
    assert b"FA23-BSE-053" in r.data
    assert b"https://github.com/ali/lab1" in r.data


def test_missing_registration_number_is_rejected(client):
    r = client.post("/submit", data={**VALID, "reg_no": ""})
    assert r.status_code == 400
    assert b"Registration number is required" in r.data
    assert b"Ali Khan" not in client.get("/").data


def test_invalid_url_is_rejected_and_not_saved(client):
    r = client.post("/submit", data={**VALID, "url": "not-a-url"})
    assert r.status_code == 400
    assert b"valid URL" in r.data
    assert b"Ali Khan" not in client.get("/").data
