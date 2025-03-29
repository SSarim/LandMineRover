# test_rover_server.py

import json
import pytest
from starlette.testclient import TestClient

from rover_server import app  # import the Flask app


# test_client_patch.py

from starlette.testclient import TestClient as BaseTestClient


class TestClient(BaseTestClient):
    def post(self, *args, **kwargs):
        if "content_type" in kwargs:
            ct = kwargs.pop("content_type")
            # Merge with any existing headers or create a new headers dict.
            kwargs.setdefault("headers", {})["Content-Type"] = ct
        return super().post(*args, **kwargs)

    def put(self, *args, **kwargs):
        if "content_type" in kwargs:
            ct = kwargs.pop("content_type")
            kwargs.setdefault("headers", {})["Content-Type"] = ct
        return super().put(*args, **kwargs)


# Test getting the current map
def test_get_map(client):
    response = client.get("/map")
    assert response.status_code == 200
    data = response.json()
    # Optionally validate details of the map structure
    assert "rows" in data or "cols" in data


# Test updating the map
def test_update_map(client):
    payload = {"rows": 6, "cols": 6}
    response = client.put("/map", data=json.dumps(payload), content_type="application/json")
    # Assuming a successful update returns 200 OK or 204 No Content
    assert response.status_code in (200, 204)


# Test creating a mine and then retrieving it
def test_create_and_get_mine(client):
    payload = {"serial": "M001", "x": 1, "y": 2}
    post_response = client.post("/mines", data=json.dumps(payload), content_type="application/json")
    assert post_response.status_code == 201
    mine = post_response.json()
    mine_id = mine.get("id")
    assert mine_id is not None

    # Fetch the created mine
    get_response = client.get(f"/mines/{mine_id}")
    assert get_response.status_code == 200
    mine_data = get_response.json()
    assert mine_data["serial"] == "M001"


# Test updating an existing mine
def test_update_mine(client):
    # First, create a mine
    payload_create = {"serial": "M002", "x": 2, "y": 3}
    post_response = client.post("/mines", data=json.dumps(payload_create), content_type="application/json")
    assert post_response.status_code == 201
    mine_id = post_response.json().get("id")
    assert mine_id is not None

    # Then, update the mine
    payload_update = {"serial": "M002-updated", "x": 3, "y": 4}
    put_response = client.put(f"/mines/{mine_id}", data=json.dumps(payload_update), content_type="application/json")
    assert put_response.status_code == 200

    # Verify the update
    get_response = client.get(f"/mines/{mine_id}")
    mine_data = get_response.json()
    assert mine_data["serial"] == "M002-updated"


# Test deleting a mine
def test_delete_mine(client):
    # Create a mine to delete
    payload = {"serial": "M003", "x": 3, "y": 4}
    post_response = client.post("/mines", data=json.dumps(payload), content_type="application/json")
    assert post_response.status_code == 201
    mine_id = post_response.json().get("id")
    assert mine_id is not None

    # Now delete the mine
    delete_response = client.delete(f"/mines/{mine_id}")
    # Depending on your API, deletion might return 200 OK or 204 No Content
    assert delete_response.status_code in (200, 204)

    # Verify that the mine no longer exists
    get_response = client.get(f"/mines/{mine_id}")
    assert get_response.status_code == 404


# Test disarming a mine
def test_disarm_mine(client):
    # Create a mine first
    payload = {"serial": "M004", "x": 4, "y": 5}
    post_response = client.post("/mines", data=json.dumps(payload), content_type="application/json")
    assert post_response.status_code == 201
    mine_id = post_response.json().get("id")
    assert mine_id is not None

    # Disarm the created mine (using a hypothetical endpoint)
    disarm_response = client.post(f"/mines/{mine_id}/disarm")
    assert disarm_response.status_code == 200
    # Optionally, verify if additional status or details have changed


# Test creating a rover and retrieving it
def test_create_and_get_rover(client):
    payload = {"commands": "FFRLF"}
    post_response = client.post("/rovers", data=json.dumps(payload), content_type="application/json")
    assert post_response.status_code == 201
    rover = post_response.json()
    rover_id = rover.get("id")
    assert rover_id is not None

    # Retrieve the created rover
    get_response = client.get(f"/rovers/{rover_id}")
    assert get_response.status_code == 200
    rover_data = get_response.json()
    assert rover_data.get("commands") == "MMRLM"


# Test updating an existing rover
def test_update_rover(client):
    # First, create a rover
    payload = {"commands": "FFRLF"}
    post_response = client.post("/rovers", data=json.dumps(payload), content_type="application/json")
    assert post_response.status_code == 201
    rover_id = post_response.json().get("id")
    assert rover_id is not None

    # Now update the rover
    update_payload = {"commands": "LRFF"}
    put_response = client.put(f"/rovers/{rover_id}", data=json.dumps(update_payload), content_type="application/json")
    assert put_response.status_code == 200

    # Verify the update
    get_response = client.get(f"/rovers/{rover_id}")
    rover_data = get_response.json()
    assert rover_data.get("commands") == "LRFF"


# Test deleting a rover
def test_delete_rover(client):
    # Create a rover first
    payload = {"commands": "FFRLF"}
    post_response = client.post("/rovers", data=json.dumps(payload), content_type="application/json")
    assert post_response.status_code == 201
    rover_id = post_response.json().get("id")
    assert rover_id is not None

    # Delete the rover
    delete_response = client.delete(f"/rovers/{rover_id}")
    assert delete_response.status_code in (200, 204)

    # Verify deletion
    get_response = client.get(f"/rovers/{rover_id}")
    assert get_response.status_code == 404


# Test dispatching a rover
def test_dispatch_rover(client):
    # Create a rover to dispatch
    payload = {"commands": "FFRLF"}
    post_response = client.post("/rovers", data=json.dumps(payload), content_type="application/json")
    assert post_response.status_code == 201
    rover_id = post_response.json().get("id")
    assert rover_id is not None

    # Dispatch the rover using a hypothetical endpoint
    dispatch_payload = {"destination": {"x": 3, "y": 3}}
    dispatch_response = client.post(
        f"/rovers/{rover_id}/dispatch",
        data=json.dumps(dispatch_payload),
        content_type="application/json"
    )
    assert dispatch_response.status_code == 200
    # Optionally, verify that the rover's position or status has been updated


# Test controlling a rover
def test_control_rover(client):
    # Create a rover to control
    payload = {"commands": "FFRLF"}
    post_response = client.post("/rovers", data=json.dumps(payload), content_type="application/json")
    assert post_response.status_code == 201
    rover_id = post_response.json().get("id")
    assert rover_id is not None

    # Control the rover (using a hypothetical control command)
    control_payload = {"command": "start"}
    control_response = client.post(
        f"/rovers/{rover_id}/control",
        data=json.dumps(control_payload),
        content_type="application/json"
    )
    assert control_response.status_code == 200
    # Optionally, you can check the rover's state after this command