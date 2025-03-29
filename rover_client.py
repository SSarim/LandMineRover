import sys
import json
import requests
import copy

# URL of the FastAPI server
SERVER_URL = "http://localhost:8000"


def simulate_rover(rover_id: int) -> bool:
    # Retrieve the map from the server
    resp = requests.get(f"{SERVER_URL}/map")
    if resp.status_code != 200:
        print("Failed to retrieve map.")
        return False
    map_data = resp.json().get("map", [])
    print("Initial Map:")
    for row in map_data:
        print(row)

    # Check if the rover exists
    resp = requests.get(f"{SERVER_URL}/rovers/{rover_id}")
    if resp.status_code == 404:
        print(f"Rover {rover_id} not found. Creating a new rover.")
        commands = input("Enter rover commands: ")
        create_resp = requests.post(f"{SERVER_URL}/rovers", json={"commands": commands})
        if create_resp.status_code != 200:
            print("Failed to create rover.")
            return False
        rover_id = create_resp.json().get("id")
        print(f"Created Rover with id: {rover_id}")
    else:
        print(f"Rover {rover_id} found.")

    # Dispatch the rover: the server will simulate the commands
    dispatch_resp = requests.post(f"{SERVER_URL}/rovers/{rover_id}/dispatch")
    if dispatch_resp.status_code != 200:
        print("Failed to dispatch rover.")
        return False

    result = dispatch_resp.json()
    rover_info = result.get("rover")
    if not rover_info:
        print("No rover info returned from dispatch.")
        return False

    print("Dispatch Result:")
    print(json.dumps(rover_info, indent=4))
    # If the rover status is "Eliminated", the simulation failed.
    return rover_info["status"] != "Eliminated"


def main():
    if len(sys.argv) != 2:
        print("Usage: python rover_client.py <rover_id>")
        sys.exit(1)
    try:
        rover_id = int(sys.argv[1])
    except ValueError:
        print("Invalid rover id. Please provide an integer.")
        sys.exit(1)

    print(f"Dispatching Rover {rover_id} via FastAPI endpoints...")
    success = simulate_rover(rover_id)
    if success:
        print("Rover simulation finished successfully.")
    else:
        print("Rover was eliminated during simulation.")


if __name__ == "__main__":
    main()
