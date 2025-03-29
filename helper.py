import json
import random
import requests
from hashlib import sha256


# Creating a grid map (Blank initially)
def generate_map_grid(row=None, col=None, update_change=True):
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

# APU Rover command
def get_rover_commands(rover_id):
    api = 'https://coe892.reev.dev/lab1/rover'
    r = requests.get(f'{api}/{rover_id}')
    if r.ok:
        content = json.loads(r.content)
        return content['data']['moves']
    else:
        raise Exception("Failed to fetch api")

# Directions
def update_direction(curr_direction, move) -> str:
    if curr_direction == "NORTH":
        if move == "L":
            return "WEST"
        else:
            return "EAST"

    elif curr_direction == "WEST":
        if move == "L":
            return "SOUTH"
        else:
            return "NORTH"

    if curr_direction == "SOUTH":
        if move == "L":
            return "EAST"
        else:
            return "WEST"

    if curr_direction == "EAST":
        if move == "L":
            return "NORTH"
        else:
            return "SOUTH"

# Deminer Disarm function for the rover
def disarm_mine(serial_num: str) -> int:
    pin = 0
    temp_mine_key = str(pin) + serial_num
    hashed_data = sha256(temp_mine_key.encode()).hexdigest()
    print(f' [-] Initial Hash: {hashed_data}')
    while True:
        if hashed_data[0:6] == '000000':
            print(f' [-] Completed Hash: {hashed_data}')
            return pin
        temp_mine_key = str(pin) + serial_num
        hashed_data = sha256(temp_mine_key.encode()).hexdigest()
        pin += 1

