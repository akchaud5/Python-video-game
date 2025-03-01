# Ping Pong Game

A customizable Ping Pong game built with Pygame featuring AI difficulty levels, customizable physics, practice mode, and integrated network multiplayer.

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

- **Integrated Network Multiplayer**
  - Play against others over a network
  - Real-time synchronization
  - Host or join games directly from the main menu
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
  - **Both Players**: Arrow Up/Down to move paddles
  - **R**: Restart after game over
  - **ESC**: Quit to main menu

## Requirements

- Python 3.x
- Pygame library
- Netifaces library (for network detection)

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
   pip install -r requirements.txt
   ```
   
   Or install manually:
   ```
   pip install pygame netifaces
   ```
   
4. Set up a virtual environment (optional but recommended):
   ```
   python -m venv myenv
   source myenv/bin/activate  # On Windows: myenv\Scripts\activate
   pip install -r requirements.txt
   ```

## Running the Game

Run the game using Python:
```
python main.py
```

### Playing Multiplayer Mode

To play multiplayer mode across different computers:

1. **Network Requirements:**
   - Both devices must be on the same network
   - **Important:** Many public WiFi networks block device-to-device communication
   - For best results, use a personal hotspot (like a phone's 5G/4G hotspot) to connect both devices
   - Corporate or university networks often block the required ports

2. Start the server on one computer:
   ```
   python server.py
   ```
   - Note the IP address displayed when the server starts 
   - The server will clearly show a "RECOMMENDED CONNECTION ADDRESS" to use
   - You can also find the local IP address using `ifconfig` (Mac/Linux) or `ipconfig` (Windows)

3. On each player's computer:
   - Run the game: `python main.py`
   - From the main menu, select "Multiplayer Mode"
   - Enter the server's IP address when prompted
     - Use "localhost" if playing on the same computer as the server
     - Use the server's IP address (from step 2) if playing on a different computer

4. Game Setup:
   - The first player to connect gets the left paddle, the second player gets the right paddle
   - Game will begin automatically once both players are connected
   - If a connection fails, the game will display an error message
   - If someone disconnects, the game will pause until both players are connected again

5. **Troubleshooting:**
   - If connection fails on a public WiFi network, try creating a personal hotspot with your phone
   - Make sure both devices are connected to the same network
   - Try restarting the server and clients
   - Check for any security software that might be blocking the connection
   - Detailed connection logs are stored in network_debug.log and server_debug.log

For playing over the internet (outside your local network):
1. The server host needs to:
   - Set up port forwarding on their router for port 5555
   - Share their public IP address (which can be found at websites like whatismyip.com)
   - Run the server as described above
   
2. Players connect using the public IP address of the host

## Building Standalone Executables

This project includes a build script to create a standalone executable using PyInstaller:

1. Run the build script:
   ```
   python build.py
   ```

2. Select option 1 to create the executable
3. Find the executable in the 'dist' directory:
   - PingPong: Complete game with single player and multiplayer modes

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