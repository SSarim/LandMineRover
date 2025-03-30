from fastapi.testclient import TestClient
from rover_server import *

client = TestClient(app)

def test_get_map():
    response = client.get("/map")
    assert response.status_code == 200
    data = response.json()
    assert "row" in data
    assert "col" in data
    assert "map" in data

def test_update_map():
    new_dimensions = {"row": 6, "col": 6}
    response = client.put("/map", json=new_dimensions)
    assert response.status_code == 201
    data = response.json()
    assert data["row"] == 6
    assert data["col"] == 6
    assert "map" in data

def test_create_and_get_mine():
    # Create a mine
    mine_payload = {"row": 2, "col": 2, "serialNum": 1234}
    response = client.post("/mines", json=mine_payload)
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    mine_id = mine_payload["serialNum"]

    # Get list of mines and check our mine is present
    response = client.get("/mines")
    assert response.status_code == 200
    data = response.json()
    mines_list = data.get("mines", [])
    assert any(m["id"] == mine_id for m in mines_list)

    # Get individual mine by id
    response = client.get(f"/mines/{mine_id}")
    assert response.status_code == 200
    mine_data = response.json()
    assert mine_data["row"] == mine_payload["row"]
    assert mine_data["col"] == mine_payload["col"]

def test_delete_mine():
    # Create a mine to delete
    mine_payload = {"row": 3, "col": 3, "serialNum": 5678}
    response = client.post("/mines", json=mine_payload)
    assert response.status_code == 200

    # Delete the mine
    response = client.delete(f"/mines/{mine_payload['serialNum']}")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data

    # Ensure the mine is no longer there
    response = client.get(f"/mines/{mine_payload['serialNum']}")
    assert response.status_code == 404

def test_create_and_get_rover():
    rover_payload = {"commands": "MRMLM"}
    response = client.post("/rovers", json=rover_payload)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    rover_id = data["id"]

    # Get the created rover
    response = client.get(f"/rovers/{rover_id}")
    assert response.status_code == 200
    rover_data = response.json()
    assert rover_data["commands"] == "MRMLM"
    assert rover_data["status"] == "ROVER IS IDLE"

    # Update rover commands
    update_payload = {"commands": "MMR"}
    response = client.put(f"/rovers/{rover_id}", json=update_payload)
    assert response.status_code == 200
    updated_data = response.json()
    assert updated_data["rover"]["commands"] == "MMR"

def test_dispatch_rover():
    # Create a rover for dispatching
    rover_payload = {"commands": "MMR"}
    response = client.post("/rovers", json=rover_payload)
    assert response.status_code == 200
    data = response.json()
    rover_id = data["id"]

    # Dispatch the rover
    response = client.post(f"/rovers/{rover_id}/dispatch")
    assert response.status_code == 200
    dispatch_data = response.json()
    assert "message" in dispatch_data
    assert "rover" in dispatch_data

def test_get_commands():
    # External API test
    response = client.get("/commands/1")
    assert response.status_code == 200
    data = response.json()
    assert "commands" in data

def test_websocket_rover_control():
    # Create a rover to control via WebSocket
    rover_payload = {"commands": "MMLD"}
    response = client.post("/rovers", json=rover_payload)
    assert response.status_code == 200
    data = response.json()
    rover_id = data["id"]

    with client.websocket_connect(f"/ws/rovers/{rover_id}") as websocket:
        # Send a move command via WebSocket and check for a valid response message
        websocket.send_text("M")
        message = websocket.receive_json()
        assert "message" in message
