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
