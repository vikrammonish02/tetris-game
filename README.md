# Tetris Game

A classic Tetris video game built with Python and Pygame. Rotate falling tetrominoes to clear lines, score points, and avoid stacking to the top. A browser version using HTML5 canvas is also included for quick play without installing dependencies.

## Features
- Seven classic tetromino shapes with rotation.
- Line clearing and scoring (100 points per cleared line).
- Game over detection when blocks reach the top.
- Next-piece preview and simple start screen.

## Play in the Browser
Open `index.html` in a modern browser to play the HTML5 Canvas version.

Controls:
- **Left/Right Arrow**: Move piece horizontally
- **Down Arrow**: Soft drop
- **Up Arrow**: Rotate piece
- **Space**: Hard drop
- **P** or **Pause button**: Pause/Resume
- **Restart button**: Start a fresh run

## Play with Pygame
- Requirements: Python 3.9+ and pygame (see `requirements.txt`).

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the game:

```bash
python tetris.py
```

Controls:
- **Left/Right Arrow**: Move piece horizontally
- **Down Arrow**: Soft drop
- **Up Arrow**: Rotate piece
- **Window close button**: Quit the game

## Run the Turbine Simulation API + Web UI

This repository also includes a FastAPI service for managing turbine simulations and a lightweight web UI.

### Quick start with Docker Compose

1. Clone the repository and move into it so Docker can see the `Dockerfile` in the project root:

```bash
git clone https://github.com/vikrammonish02/tetris-game.git
cd tetris-game
```

2. Build and start the stack (runs the OpenFAST image build plus the FastAPI service and PostgreSQL):

```bash
docker compose up --build
```

Once the stack is running:

- Visit http://localhost:8000/ to open the simulation manager web UI.
- The API schema is available at http://localhost:8000/docs.

### Standalone image build

If you prefer to build the app image directly (without Compose), run this from the repository root so Docker can find the `Dockerfile`:

```bash
docker build -t tetris-game:latest .
```

### Local development without Docker

```bash
pip install -r requirements.txt
uvicorn simulation_api:app --reload
```

The service runs on http://127.0.0.1:8000/ with the same endpoints as above.
