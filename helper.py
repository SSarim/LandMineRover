# Sarim Shahwar
import hashlib
import json
import random
import requests

def generate_map_grid(row, col, update_change=True):
    grid = []
    mines = []
    if update_change:
        for i in range(row):
            grid.append([0] * col)
        return grid, mines
    else:
        serial_num_list = random.sample(range(1000, 10000), 9000)
        for i in range(row):
            curr_row = []
            for j in range(col):
                if random.randint(1, 10) < 3:
                    mines.append([i, j, serial_num_list.pop()])
                    curr_row.append(1)
                else:
                    curr_row.append(0)
            grid.append(curr_row)
        return grid, mines

def get_rover_commands(rover_id):
    api = 'https://coe892.reev.dev/lab1/rover'
    r = requests.get(f'{api}/{rover_id}')
    if r.ok:
        content = json.loads(r.content)
        return content['data']['moves']
    else:
        raise Exception("Failed to fetch API")

# added as it's a pain to use numbers as directions :P
direction_map = ["North", "East", "South", "West"]
def format_response_message(response: dict) -> str:
    if "error" in response:
        return f"❌ Error: {response['error']}"
    elif response["command"] == "M":
        if response["result"]:
            return f"✅ Move successful → New Position: {response['new_position']}"
        else:
            return f"❌ Move failed: {response['error']}"
    elif response["command"] == "L":
        return f"↩️ Turned Left → New Direction: {direction_map[response['direction']]}"
    elif response["command"] == "R":
        return f"↪️ Turned Right → New Direction: {direction_map[response['direction']]}"
    elif response["command"] == "D":
        if response.get("result"):
            return f"🛠️ Disarmed Mine → PIN: {response['pin']}"
        else:
            return f"❌ Disarm Failed: {response['error']}"
    return f"ℹ️ Executed Command: {response['command']}"

# Deminer (from prev testing)
def disarm_mine(serial) -> str:
    serial = str(serial)
    pin = 0
    while True:
        candidate = str(pin)
        temp_key = serial + candidate
        hashed = hashlib.sha256(temp_key.encode('utf-8')).hexdigest()
        if hashed.startswith("000000"):
            return candidate
        pin += 1
