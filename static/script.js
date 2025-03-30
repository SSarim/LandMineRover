// Sarim Shahwar
const serverUrl = "http://localhost:8000";
async function loadMap() {
    const res = await fetch(serverUrl + "/map");
    const data = await res.json();
    const map = data.map;
    const container = document.getElementById("map-container");
    container.innerHTML = "";
    const table = document.createElement("table");

    // Column headers
    const headerRow = document.createElement("tr");
    headerRow.appendChild(document.createElement("th")); // Empty corner cell
    for (let c = 0; c < map[0].length; c++) {
        const th = document.createElement("th");
        th.textContent = c;
        th.style.background = "#f0f0f0";
        th.style.fontWeight = "bold";
        headerRow.appendChild(th);
    }
    table.appendChild(headerRow);

    // Rows with row headers
    for (let r = 0; r < map.length; r++) {
        const row = document.createElement("tr");

        // Row number header
        const rowHeader = document.createElement("th");
        rowHeader.textContent = r;
        rowHeader.style.background = "#f0f0f0";
        rowHeader.style.fontWeight = "bold";
        row.appendChild(rowHeader);

        for (let c = 0; c < map[r].length; c++) {
            const cell = document.createElement("td");
            if (map[r][c] === 1) {
                cell.textContent = "💣";
                cell.classList.add("mine");
            } else if (map[r][c] === 2) {
                cell.textContent = "🤖";
                cell.classList.add("rover-path");
            } else {
                cell.textContent = "";
            }
            cell.addEventListener("click", () => {
                document.getElementById("mine-x").value = c;
                document.getElementById("mine-y").value = r;
            });
            row.appendChild(cell);
        }
        table.appendChild(row);
    }
    container.appendChild(table);
}

async function loadMines() {
    const res = await fetch(serverUrl + "/mines");
    const data = await res.json();
    const minesList = document.getElementById("mines1");
    minesList.innerHTML = "<h4>🧾 Existing Mines</h4>";
    data.mines.forEach(mine => {
        const div = document.createElement("div");
        div.textContent = `💣 ID: ${mine.id} — (Y: ${mine.row}, X: ${mine.col})`;
        minesList.appendChild(div);
    });
}

async function loadRovers() {
    const res = await fetch(serverUrl + "/rovers");
    const data = await res.json();
    const roversList = document.getElementById("rovers-list");
    roversList.innerHTML = "<h4>🧾 Rover Fleet</h4>";
    data.rovers.forEach(rover => {
        const div = document.createElement("div");
        div.textContent = `🤖 ID: ${rover.id} — Status: ${rover.status}`;
        roversList.appendChild(div);
    });
}

// Event Listeners for Map, Mine and Rover forms
document.getElementById("refresh-map-btn").addEventListener("click", loadMap);
document.getElementById("create-mine-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const serialNum = parseInt(document.getElementById("mine-serial").value);
    const row = parseInt(document.getElementById("mine-y").value);
    const col = parseInt(document.getElementById("mine-x").value);
    const res = await fetch(serverUrl + "/mines", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({row, col, serialNum})
    });
    const data = await res.json();
    alert(data.message);
    loadMap();
    loadMines();
});

document.getElementById("create-rover-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const commands = document.getElementById("rover-commands").value;
    // Set initial position and facing South (2)
    const initialX = 0;
    const initialY = 0;
    const initialDirection = 2;
    const res = await fetch(serverUrl + "/rovers", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            commands,
            x: initialX,
            y: initialY,
            direction: initialDirection
        })
    });
    const data = await res.json();
    alert(data.message + " ID: " + data.id);
    loadRovers();
});

document.getElementById("dispatch-rover-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const dispatchStatus = document.getElementById("dispatch-status");
    const dispatchBtn = document.getElementById("dispatch-btn");
    dispatchStatus.textContent = "Dispatching Rover...";
    dispatchBtn.disabled = true;
    const rover_id = document.getElementById("dispatch-rover-id").value;
    const res = await fetch(serverUrl + "/rovers/" + rover_id + "/dispatch", {method: "POST"});
    const data = await res.json();
    alert(data.message);
    dispatchStatus.textContent = "";
    dispatchBtn.disabled = false;
    loadRovers();
    loadMines();
    loadMap();
});

// WebSocket for real-time rover control
let ws;
document.getElementById("open-ws-btn").addEventListener("click", async () => {
    const rover_id = prompt("Enter Created Rover ID for WebSocket control:");
    if (!rover_id) return;
    ws = new WebSocket("ws://localhost:8000/ws/rovers/" + rover_id);
    ws.onopen = () => {
        document.getElementById("ws-status").textContent = "Connected";
        document.getElementById("ws-control").style.display = "block";
        document.getElementById("live-status").textContent = "🟢 Online";
        document.getElementById("live-status").style.color = "#27ae60";
    };
    ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        const wsMessages = document.getElementById("ws-messages");
        const div = document.createElement("div");
        div.textContent = msg.message;
        wsMessages.appendChild(div);
        wsMessages.scrollTop = wsMessages.scrollHeight;
        loadMap();
        loadMines();
        loadRovers();
    };
    ws.onclose = () => {
        document.getElementById("ws-status").textContent = "Disconnected";
        document.getElementById("live-status").textContent = "🔴 Offline";
        document.getElementById("live-status").style.color = "#c0392b";
    };
});

document.querySelectorAll(".ws-cmd").forEach(button => {
    button.addEventListener("click", () => {
        const cmd = button.getAttribute("data-cmd");
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(cmd);
        } else {
            alert("WebSocket is not connected");
        }
    });
});

loadMap();
loadMines();
loadRovers();
