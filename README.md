# 🛰️ Rover Demining Operator Dashboard

A web-based control center to manage autonomous rovers for minefield demining simulation. Built with FastAPI, Jinja2, and WebSockets, with a bases of Python, JavaScript, Docker and Azure  — featuring real-time rover control and interactive map updates.

🌐 Live Demo: [Rover Server on Azure](https://roverserver-cfgfa8g0hphmd6af.canadacentral-01.azurewebsites.net/)

---

## 🚀 Features

- 🌍 **Map Grid Visualization** — View and interact with a dynamic minefield map
- 💣 **Mine Management** — Add, view, update, and delete mines via API or UI
- 🤖 **Rover Management** — Create rovers, assign command sequences, dispatch them
- 🧠 **Mine Disarming Logic** — Auto-generates PINs using a hash-based proof-of-work
- 📡 **Real-time Control** — WebSocket interface for direct rover command control
- 🔍 **Command Feedback** — Interactive logs with directional updates and errors
- ✅ **Fully Tested** — Includes test suite using FastAPI's `TestClient`

---

## 🧰 Tech Stack

- **Backend:** Python, FastAPI, Starlette, Pydantic, Uvicorn
- **Frontend:** JavaScript, Pico.css, HTML/CSS
- **Others:** WebSockets, Jinja2 Templates, SHA256 hashing
- **Past Versions:** gRPC, RabbitMQ

---

## 📂 Project Structure

```
.
├── rover_server.py         # FastAPI main app and endpoints
├── helper.py               # Utilities for grid, mine handling, and command parsing
├── rover_api_test_suite.py # End-to-end and unit tests
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker configuration
├── templates/
│   └── index.html          # Main HTML template
├── static/
│   ├── design.css          # Styling
│   └── script.js           # Frontend logic and API integration
```

---

## 🧪 Local Development

### 1. Clone and Setup

```bash
git clone https://github.com/SSarim/LandMineRover.git
cd LandMineRover
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the Server

```bash
uvicorn rover_server:app --reload
```

Visit: [http://localhost:8000](http://localhost:8000) for local usage.

---

## 🧪 Running Tests

```bash
pytest rover_api_test_suite.py
```

---

## 🐳 Docker Deployment

To containerize the app:

```bash
docker build -t roverserver:latest .
docker run --name RoverServer -p 8000:8000 roverserver:latest
```
If you need to start the server once created initially:
```bash
docker start RoverServer
```

---

## 🔧 API Endpoints Overview

| Method | Endpoint                   | Description                          |
|--------|----------------------------|--------------------------------------|
| GET    | `/map`                     | Fetch current grid                   |
| PUT    | `/map`                     | Update grid dimensions               |
| GET    | `/mines`                   | List all mines                       |
| POST   | `/mines`                   | Create a new mine                    |
| DELETE | `/mines/{id}`              | Remove a mine                        |
| GET    | `/rovers`                  | List all rovers                      |
| POST   | `/rovers`                  | Create a new rover                   |
| PUT    | `/rovers/{id}`             | Update rover commands                |
| POST   | `/rovers/{id}/dispatch`    | Dispatch rover to execute commands  |
| GET    | `/commands/{id}`           | Fetch external rover commands        |
| WS     | `/ws/rovers/{id}`          | WebSocket: real-time control         |

---

## 📬 Contributions

Feel free to fork, suggest improvements, or file issues. Feedback and contributions are welcome!

---

## 👨‍💻 Author

**Sarim Shahwar** — *April 2025*  
[LinkedIn](https://www.linkedin.com/in/sarimshahwar/) • [GitHub](https://github.com/SSarim/)

---

