# Ping Pong Game

A customizable Ping Pong game built with Pygame featuring AI difficulty levels, customizable physics, and practice mode.

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

- **Game Controls**
  - **↑/↓**: Move paddle up/down
  - **P**: Pause/unpause game
  - **ESC**: Quit game
  
  Practice Mode:
  - **SPACE**: Reset ball position
  - **W/S**: Adjust vertical ball speed
  - **A/D**: Adjust horizontal ball speed

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

Run the game using Python:
```
python main.py
```

## Game Rules

- In normal mode, the first player to reach 31 points wins
- The ball bounces off paddles and walls
- Ball speed gradually increases during play
- Ball direction changes based on where it hits the paddle

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