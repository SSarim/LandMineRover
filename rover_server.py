from fastapi import FastAPI, status, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import helper
import random
import threading
import hashlib

# SET UP
app = FastAPI()
origins = [
    # "http://localhost.*",
    # "https://localhost/*",
    # "http://localhost:80",
    # "http://localhost:8080",
    "http://localhost:8000",
    # "https://coe892lab42024g.azurewebsites.net/*"
]
# Rover statuses
ROVER_IDLE = "ROVER IS IDLE"
ROVER_OPERATION_FINISHED = "ROVER OPERATION HAS COMPLETED"
ROVER_MOVING = "ROVER IS MOVING"
ROVER_STATUS_ELIMINATED = "ROVER STATUS: ELIMINATED"

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files directory and use created front end index.html
app.mount("/static", StaticFiles(directory="templates", html=True), name="static")
templates = Jinja2Templates(directory="templates")
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Global data notations --> map, mines, rovers, commands
grid, mines = helper.generate_map_grid(row=5, col=10, update_change=True)
rovers = []  # Dict key of: id, commands, status, position, executed_commands
commands = [helper.get_rover_commands(i) for i in range(1, 11)]
id_list = random.sample(range(100, 1000), 900)
valid_commands = ['L', 'R', 'M', 'D']
state_lock = threading.Lock()

# Pydantic Model Setup
class MapDimensions(BaseModel):
    row: int
    col: int

class MineCreate(BaseModel):
    row: int
    col: int
    serialNum: int

class MineUpdate(BaseModel):
    row: Optional[int] = None
    col: Optional[int] = None
    serialNum: Optional[int] = None

class RoverCreate(BaseModel):
    commands: str

class RoverUpdate(BaseModel):
    commands: str

# Endpoints (Map)
@app.get("/map", status_code=status.HTTP_200_OK)
def get_map():
    with state_lock:
        return {
            "row": len(grid),
            "col": len(grid[0]),
            "map": grid
        }

@app.put("/map", status_code=status.HTTP_201_CREATED)
def update_map(dim: MapDimensions):
    global grid, mines
    with state_lock:
        grid, mines = helper.generate_map_grid(row=dim.row, col=dim.col)
        grid[0][0] = 0
        return {"message": "Map updated", "row": len(grid), "col": len(grid[0]), "map": grid}

# Endpoints (Mines)
@app.get("/mines")
def get_mines_endpoint():
    with state_lock:
        mines1 = [{"row": m[0], "col": m[1], "id": m[2]} for m in mines]
        return {"mines": mines1}

@app.get("/mines/{id}")
def get_mine_endpoint(id: int):
    with state_lock:
        for m in mines:
            if m[2] == id:
                return {"row": m[0], "col": m[1], "id": m[2]}
        raise HTTPException(status_code=404, detail="Mine not found")

@app.delete("/mines/{id}")
def delete_mine_endpoint(id: int):
    global mines
    with state_lock:
        for i, m in enumerate(mines):
            if m[2] == id:
                row, col = m[0], m[1]
                grid[row][col] = 0
                mines.pop(i)
                return {"message": "Mine deleted"}
        raise HTTPException(status_code=404, detail="Mine not found")

@app.post("/mines")
def create_mine_endpoint(new_mine: MineCreate):
    with state_lock:
        if grid[new_mine.row][new_mine.col]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mine already exists at the given location")
        grid[new_mine.row][new_mine.col] = 1
        mines.append([new_mine.row, new_mine.col, new_mine.serialNum])
        return {"message": "Mine created", "id": new_mine.serialNum}

@app.put("/mines/{id}")
def update_mine_endpoint(id: int, mine_update: MineUpdate):
    with state_lock:
        for i, m in enumerate(mines):
            if m[2] == id:
                new_row = mine_update.row if mine_update.row is not None else m[0]
                new_col = mine_update.col if mine_update.col is not None else m[1]
                new_serial = mine_update.serialNum if mine_update.serialNum is not None else m[2]
                grid[m[0]][m[1]] = 0
                if not (0 <= new_row < len(grid) and 0 <= new_col < len(grid[0])):
                    raise HTTPException(status_code=400, detail="New coordinates out of bounds")
                grid[new_row][new_col] = 1
                mines[i] = [new_row, new_col, new_serial]
                return {"message": "Mine updated", "row": new_row, "col": new_col, "id": new_serial}
        raise HTTPException(status_code=404, detail="Mine not found")

# Endpoints (Rover)
@app.get("/rovers")
def get_rovers_endpoint():
    with state_lock:
        return {"rovers": rovers}

@app.get("/rovers/{id}")
def get_rover_endpoint(id: int):
    with state_lock:
        for rover in rovers:
            if rover["id"] == id:
                return rover
        raise HTTPException(status_code=404, detail="Rover not found")

@app.post("/rovers")
def create_rover_endpoint(rover_data: RoverCreate):
    with state_lock:
        cmd_str = rover_data.commands.upper()
        for cmd in cmd_str:
            if cmd not in valid_commands:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid command in command list")
        new_id = id_list.pop()
        rover = {
            "id": new_id,
            "commands": cmd_str,
            "status": ROVER_IDLE,
            "position": (0, 0),
            "executed_commands": "",
            "direction": 2
        }
        rovers.append(rover)
        return {"message": "New Rover created", "id": new_id}

@app.delete("/rovers/{id}")
def delete_rover_endpoint(id: int):
    with state_lock:
        for i, rover in enumerate(rovers):
            if rover["id"] == id:
                rovers.pop(i)
                return {"message": "Rover deleted"}
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Rover with id {id} not found")

@app.put("/rovers/{id}")
def update_rover_endpoint(id: int, rover_update: RoverUpdate):
    with state_lock:
        for rover in rovers:
            if rover["id"] == id:
                if rover["status"] not in [ROVER_IDLE, ROVER_OPERATION_FINISHED]:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot update commands while rover is in progress")
                new_cmd = rover_update.commands.upper()
                for cmd in new_cmd:
                    if cmd not in valid_commands:
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid command in command list")
                rover["commands"] = new_cmd
                rover["executed_commands"] = ""
                rover["status"] = ROVER_IDLE
                rover["position"] = (0, 0)
                return {"message": "Rover commands updated", "rover": rover}
        raise HTTPException(status_code=404, detail="Rover not found")

@app.post("/rovers/{id}/dispatch")
def dispatch_rover_endpoint(id: int):
    with state_lock:
        for rover in rovers:
            if rover["id"] == id:
                if rover["status"] not in [ROVER_IDLE, ROVER_OPERATION_FINISHED]:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rover is already in progress")
                r, c = 0, 0
                direction = 2  # Starting facing south.
                executed = ""
                for cmd in rover["commands"]:
                    if grid[r][c] != 0:
                        mine_found = None
                        for m in mines:
                            if m[0] == r and m[1] == c:
                                mine_found = m
                                break
                        if mine_found:
                            if cmd == "D":
                                pin = disarm_mine(mine_found[2])
                                executed += cmd
                                mines.remove(mine_found)
                                grid[r][c] = 0
                            else:
                                executed += cmd
                                rover["status"] = ROVER_STATUS_ELIMINATED
                                rover["executed_commands"] = executed
                                rover["position"] = (r, c)
                                return {"message": "Rover exploded upon encountering a mine", "rover": rover}
                        else:
                            executed += cmd
                    else:
                        if cmd == "L":
                            direction = (direction - 1) % 4
                            executed += cmd
                        elif cmd == "R":
                            direction = (direction + 1) % 4
                            executed += cmd
                        elif cmd == "M":
                            nr, nc = r, c
                            if direction == 0:
                                nr -= 1
                            elif direction == 1:
                                nc += 1
                            elif direction == 2:
                                nr += 1
                            elif direction == 3:
                                nc -= 1
                            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                                r, c = nr, nc
                            executed += cmd
                        elif cmd == "D":
                            executed += cmd
                rover["status"] = ROVER_OPERATION_FINISHED
                rover["executed_commands"] = executed
                rover["position"] = (r, c)
                return {"message": "Rover dispatched successfully", "rover": rover}
        raise HTTPException(status_code=404, detail="Rover not found")

@app.get("/commands/{id}")
def get_commands_endpoint(id: int):
    return {"commands": helper.get_rover_commands(id)}

# Endpoint (WebSockets)
@app.websocket("/ws/rovers/{id}")
async def websocket_control_rover(websocket: WebSocket, id: int):
    await websocket.accept()
    with state_lock:
        target_rover = None
        for rover in rovers:
            if rover["id"] == id:
                target_rover = rover
                break
        if target_rover is None:
            await websocket.send_json({"error": "Rover was not found"})
            await websocket.close()
            return
        if target_rover["status"] not in [ROVER_IDLE, ROVER_OPERATION_FINISHED]:
            await websocket.send_json({"error": "Rover is not ready for real-time control"})
            await websocket.close()
            return
        target_rover["commands"] = ""
        target_rover["executed_commands"] = ""
        target_rover["position"] = (0, 0)
        target_rover["status"] = ROVER_MOVING
    direction = 2
    r, c = 0, 0
    try:
        while True:
            data = await websocket.receive_text()
            cmd = data.strip().upper()
            response = {}
            should_explode = False

            with state_lock:
                # Check if there's a mine at the current position.
                mine_found = None
                if grid[r][c] != 0:
                    for m in mines:
                        if m[0] == r and m[1] == c:
                            mine_found = m
                            break

                # If on a mine and the command is not "D", the rover explodes.
                if mine_found and cmd != "D":
                    target_rover["executed_commands"] += cmd
                    target_rover["status"] = ROVER_STATUS_ELIMINATED
                    target_rover["position"] = (r, c)
                    response = {
                        "command": cmd,
                        "result": False,
                        "error": "Rover exploded upon encountering a mine"
                    }
                    should_explode = True
                else:
                    # Process commands normally.
                    if cmd == "L":
                        direction = (direction - 1) % 4
                        response = {"command": "L", "result": True, "direction": direction}
                    elif cmd == "R":
                        direction = (direction + 1) % 4
                        response = {"command": "R", "result": True, "direction": direction}
                    elif cmd == "M":
                        nr, nc = r, c
                        if direction == 0:
                            nr -= 1
                        elif direction == 1:
                            nc += 1
                        elif direction == 2:
                            nr += 1
                        elif direction == 3:
                            nc -= 1
                        if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                            r, c = nr, nc
                            response = {"command": "M", "result": True, "new_position": [r, c]}
                        else:
                            response = {"command": "M", "result": False, "error": "Out of bounds"}
                    elif cmd == "D":
                        if mine_found:
                            # Disarm the mine if it exists.
                            pin = disarm_mine(mine_found[2])
                            response = {"command": "D", "result": True, "pin": pin}
                            mines.remove(mine_found)
                            grid[r][c] = 0
                        else:
                            response = {"command": "D", "result": False, "error": "No mine at current position"}
                    else:
                        response = {"error": "Invalid command"}

                    target_rover["executed_commands"] += cmd
                    target_rover["position"] = (r, c)

            # Send the response to the client.
            await websocket.send_json(response)

            # If the rover exploded, close the websocket.
            if should_explode:
                await websocket.close()
                return

    except WebSocketDisconnect:
        with state_lock:
            target_rover["status"] = ROVER_OPERATION_FINISHED
        return


# Disarming Mine (similar to Deminer)
def disarm_mine(serial) -> str:
    serial = str(serial)  # Convert the mine serial to a string
    pin = 0
    while True:
        candidate = str(pin)
        temp_key = serial + candidate
        hashed = hashlib.sha256(temp_key.encode('utf-8')).hexdigest()
        if hashed.startswith("000000"):
            return candidate
        pin += 1
