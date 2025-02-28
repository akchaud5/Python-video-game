# Ping Pong Game

A customizable Ping Pong game built with Pygame featuring AI difficulty levels, customizable physics, practice mode, and network multiplayer.

## Features

- **Multiple Difficulty Levels**
  - Easy: Slower AI with occasional mistakes
  - Medium: Standard AI response and tracking
  - Hard: Advanced AI that predicts ball trajectory

- **Customizable Physics**
  - Adjustable ball speed
  - Bounce energy settings
  - Paddle power controls
  - Optional gravity effects

- **Practice Mode**
  - No scoring
  - Real-time ball speed display
  - Ball control adjustments (speed and direction)
  - Reset ball position at any time

- **Network Multiplayer**
  - Play against others over a network
  - Real-time synchronization
  - Player vs Player gameplay

- **Game Controls**
  - **↑/↓**: Move paddle up/down
  - **P**: Pause/unpause game
  - **ESC**: Quit game
  - **H**: Return to home screen
  
  Practice Mode:
  - **SPACE**: Reset ball position
  - **W/S**: Adjust vertical ball speed
  - **A/D**: Adjust horizontal ball speed
  
  Multiplayer Mode:
  - **Player 1**: W/S keys to move
  - **Player 2**: Arrow Up/Down to move
  - **SPACE**: Ready up
  - **R**: Restart after game over

## Requirements

- Python 3.x
- Pygame library

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/akchaud5/Ping-Pong.git
   ```

2. Navigate to the project directory:
   ```
   cd Ping-Pong
   ```

3. Install the required dependencies:
   ```
   pip install pygame
   ```

## Running the Game

### Single Player
Run the game using Python:
```
python main.py
```

### Multiplayer

1. Start the server on one computer:
   ```
   python server.py
   ```

2. Start the multiplayer client on each player's computer:
   ```
   python multiplayer.py
   ```
   
   By default, the game connects to localhost. To connect to a remote server,
   edit the server address in network.py.

## Building Standalone Executables

This project includes a build script to create standalone executables using PyInstaller:

1. Run the build script:
   ```
   python build.py
   ```

2. Select option 1 to create executables
3. Find the executables in the 'dist' directory

## Game Rules

- In single player mode, the first player to reach 8 points wins
- In multiplayer mode, the first player to reach 8 points wins
- The ball bounces off paddles and walls
- Ball speed gradually increases during play
- Ball direction changes based on where it hits the paddle
- Practice mode has no scoring and allows for ball control practice

## Physics Customization

Access the Physics Settings from the main menu to adjust:
- Ball speed multiplier (0.5x to 2.0x)
- Bounce energy (how much momentum is retained on bounce)
- Paddle power (how strongly paddles affect ball trajectory)
- Gravity (optional downward pull on the ball)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Pygame](https://www.pygame.org/)