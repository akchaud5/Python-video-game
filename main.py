import pygame
from pygame.locals import *
import random
import sys
import socket
import pickle
import threading
import time

# Import network module for multiplayer
from network import Network

# Server class for multiplayer host
class GameState:
    def __init__(self):
        # Screen dimensions
        self.width = 800
        self.height = 600
        
        # Paddle dimensions
        self.paddle_width = 20
        self.paddle_height = 100
        
        # Default paddle positions 
        self.left_paddle_y = self.height // 2 - self.paddle_height // 2
        self.right_paddle_y = self.height // 2 - self.paddle_height // 2
        
        # Ball settings
        self.ball_size = 20
        self.ball_x = self.width // 2 - self.ball_size // 2
        self.ball_y = self.height // 2 - self.ball_size // 2
        self.ball_speed_x = 5 * random.choice([-1, 1])
        self.ball_speed_y = random.randint(-5, 5)
        
        # Scores
        self.left_score = 0
        self.right_score = 0
        
        # Game status
        self.game_active = False
        self.winner = ""

    def update_ball(self):
        if not self.game_active:
            return
            
        # Move the ball
        self.ball_x += self.ball_speed_x
        self.ball_y += self.ball_speed_y
        
        # Ball collision with top and bottom walls
        if self.ball_y <= 0:
            self.ball_y = 0
            self.ball_speed_y = -self.ball_speed_y
        elif self.ball_y + self.ball_size >= self.height:
            self.ball_y = self.height - self.ball_size
            self.ball_speed_y = -self.ball_speed_y
            
        # Check for paddle collisions
        # Left paddle collision
        if (self.ball_x <= 50 + self.paddle_width and 
            self.ball_x + self.ball_size >= 50 and 
            self.ball_y + self.ball_size >= self.left_paddle_y and 
            self.ball_y <= self.left_paddle_y + self.paddle_height):
            
            hit_pos = (self.ball_y + self.ball_size/2 - (self.left_paddle_y + self.paddle_height/2)) / (self.paddle_height/2)
            self.ball_speed_y = hit_pos * 5
            self.ball_speed_x = -self.ball_speed_x
            self.ball_x = 50 + self.paddle_width + 1
            
        # Right paddle collision
        if (self.ball_x + self.ball_size >= self.width - 50 - self.paddle_width and 
            self.ball_x <= self.width - 50 and
            self.ball_y + self.ball_size >= self.right_paddle_y and 
            self.ball_y <= self.right_paddle_y + self.paddle_height):
            
            hit_pos = (self.ball_y + self.ball_size/2 - (self.right_paddle_y + self.paddle_height/2)) / (self.paddle_height/2)
            self.ball_speed_y = hit_pos * 5
            self.ball_speed_x = -self.ball_speed_x
            self.ball_x = self.width - 50 - self.paddle_width - self.ball_size - 1
            
        # Scoring
        if self.ball_x <= 0:
            self.right_score += 1
            self.reset_ball()
        elif self.ball_x + self.ball_size >= self.width:
            self.left_score += 1
            self.reset_ball()
            
        # Check win condition
        if self.left_score > 7:
            self.winner = "Player 1 Wins!"
            self.game_active = False
        elif self.right_score > 7:
            self.winner = "Player 2 Wins!"
            self.game_active = False

    def reset_ball(self):
        self.ball_x = self.width // 2 - self.ball_size // 2
        self.ball_y = self.height // 2 - self.ball_size // 2
        self.ball_speed_x = 5 * random.choice([-1, 1])
        self.ball_speed_y = random.randint(-5, 5)

    def start_game(self):
        self.left_score = 0
        self.right_score = 0
        self.reset_ball()
        self.winner = ""
        self.game_active = True

class Server:
    def __init__(self, host='', port=5555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        self.host = host
        self.port = port
        
        try:
            self.server.bind((self.host, self.port))
        except socket.error as e:
            print(f"Socket Binding error: {e}")
            
        self.server.listen(2)
        print(f"Server started, waiting for connection on port {self.port}...")
        
        self.connections = {}
        self.players_ready = set()
        self.game_state = GameState()
        self.game_thread = None
        self.game_running = False

    def handle_client(self, conn, player_id):
        # Send initial player ID
        conn.send(pickle.dumps(player_id))
        
        try:
            while True:
                try:
                    # Receive paddle position from client
                    data = conn.recv(2048)
                    if not data:  # Connection closed
                        print(f"No data received from Player {player_id}")
                        break
                        
                    data = pickle.loads(data)
                    
                    if data == "ready":
                        print(f"Player {player_id} is ready")
                        self.players_ready.add(player_id)
                        print(f"Ready players: {self.players_ready}")
                        # If both players are ready, start the game
                        if len(self.players_ready) == 2 and not self.game_running:
                            print("Both players ready! Starting game...")
                            self.start_game_thread()
                    
                    elif data == "restart":
                        self.game_state.start_game()
                    
                    elif data is not None:  # Regular paddle update
                        # Update paddle position based on player
                        if player_id == 0:  # Player 1 (left paddle)
                            self.game_state.left_paddle_y = data
                        else:  # Player 2 (right paddle)
                            self.game_state.right_paddle_y = data
                    
                    # Send current game state to the client
                    conn.send(pickle.dumps(self.game_state))
                    
                except ConnectionResetError:
                    print(f"Connection reset by Player {player_id}")
                    break
                except Exception as e:
                    print(f"Error in client handler: {e}")
                    break
                    
        finally:
            print(f"Player {player_id} disconnected")
            if player_id in self.players_ready:
                self.players_ready.remove(player_id)
            if player_id in self.connections and self.connections[player_id] == conn:
                del self.connections[player_id]
            try:
                conn.close()
            except:
                pass
            
    def start_game_thread(self):
        print("Starting game thread - setting game_active to True")
        self.game_running = True
        self.game_state.start_game()
        print(f"Game state is now: active={self.game_state.game_active}, ball_pos=({self.game_state.ball_x}, {self.game_state.ball_y})")
        self.game_thread = threading.Thread(target=self.game_loop)
        self.game_thread.daemon = True
        self.game_thread.start()
        print("Game thread started successfully")
        
    def game_loop(self):
        last_time = time.time()
        loop_count = 0
        
        while self.game_running:
            loop_count += 1
            if loop_count % 60 == 0:  # Log every second (assuming 60 FPS)
                print(f"Game loop running. Ball position: ({self.game_state.ball_x}, {self.game_state.ball_y})")
            
            # Check if we have two players connected
            if len(self.connections) < 2:
                print("Game paused: waiting for two players")
                time.sleep(1)  # Check every second
                continue
                
            # Control game speed (60 FPS)
            current_time = time.time()
            dt = current_time - last_time
            if dt < 1/60:
                time.sleep(1/60 - dt)
                
            self.game_state.update_ball()
            last_time = time.time()
            
            # If game is over, stop the game loop
            if not self.game_state.game_active:
                self.game_running = False
                
        print("Game loop ended")
        self.players_ready.clear()
        
    def start(self):
        current_player = 0
        
        while True:
            conn, addr = self.server.accept()
            print(f"Connected to: {addr}")
            
            # Only accept two players
            if len(self.connections) < 2:
                # If player ID is already in use, find an available ID
                if current_player in self.connections:
                    current_player = 0 if current_player == 1 else 1
                
                # Store connection and start client handler thread
                self.connections[current_player] = conn
                threading.Thread(target=self.handle_client, args=(conn, current_player)).start()
                current_player = (current_player + 1) % 2
            else:
                print(f"Rejected connection from {addr}: server full")
                conn.close()

# Initialize Pygame
pygame.init()

# Set up the screen
width = 800
height = 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Ping Pong")

# Define colors
black = (0, 0, 0)
white = (255, 255, 255)
gray = (150, 150, 150)
green = (0, 255, 0)
yellow = (255, 255, 0)
red = (255, 0, 0)

# Physics settings
ball_base_speed = 5  # Base ball speed (will be modified by settings)
ball_speed_multiplier = 1.0  # Multiplier for ball speed
gravity_enabled = False  # Option to enable gravity
bounce_dampening = 1.0  # How much energy is retained on bounce (1.0 = perfect bounce)
paddle_rebound_strength = 1.0  # How strongly paddles affect ball trajectory

# Create paddles
paddle_width = 20
paddle_height = 100
left_paddle = pygame.Rect(50, height//2 - paddle_height//2, paddle_width, paddle_height)
right_paddle = pygame.Rect(width - 50 - paddle_width, height//2 - paddle_height//2, paddle_width, paddle_height)

# Create ball
ball_size = 20
ball = pygame.Rect(width//2 - ball_size//2, height//2 - ball_size//2, ball_size, ball_size)

# Set initial ball speed
ball_speed_x = ball_base_speed * ball_speed_multiplier * random.choice([-1, 1])
ball_speed_y = random.randint(-int(ball_base_speed), int(ball_base_speed)) * ball_speed_multiplier

# Initialize dragging flags
dragging_speed = False
dragging_bounce = False
dragging_rebound = False

# Set scores
left_score = 0
right_score = 0

# Set up font for text rendering
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)

# Game state variables
game_over = False
winner = ""
game_started = False
paused = False
settings_screen = False
practice_mode = False
difficulty = "medium"  # Default difficulty
ai_speed = 5  # Default AI speed for medium difficulty

# Physics settings
ball_base_speed = 5  # Base ball speed (will be modified by settings)
ball_speed_multiplier = 1.0  # Multiplier for ball speed
gravity_enabled = False  # Option to enable gravity
bounce_dampening = 1.0  # How much energy is retained on bounce (1.0 = perfect bounce)
paddle_rebound_strength = 1.0  # How strongly paddles affect ball trajectory

# Function to reset the ball to the center
def reset_ball():
    global ball_speed_x, ball_speed_y
    ball.center = (width//2, height//2)
    ball_speed_x = ball_base_speed * ball_speed_multiplier * random.choice([-1, 1])
    ball_speed_y = random.randint(-int(ball_base_speed), int(ball_base_speed)) * ball_speed_multiplier
    
# Function to run multiplayer mode
def run_multiplayer_mode():
    # Set up fonts for the multiplayer mode
    multiplayer_font = pygame.font.Font(None, 74)
    multiplayer_small_font = pygame.font.Font(None, 36)
    
    # Ask for server IP if not localhost
    server_ip = "localhost"  # Default to localhost
    
    # Try to provide a default server IP suggestion from the local network
    suggested_ip = ""
    try:
        # Try to get a default IP that's not localhost or 127.0.0.1
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Doesn't need to be reachable, just used to get local interface
            s.connect(('10.255.255.255', 1))
            suggested_ip = s.getsockname()[0]
            if suggested_ip == "127.0.0.1":
                suggested_ip = ""
        except:
            pass
        finally:
            s.close()
    except:
        pass
    
    # Simple dialog for server IP input
    pygame.draw.rect(screen, black, (0, 0, width, height))
    title_text = multiplayer_font.render("Multiplayer Setup", True, white)
    screen.blit(title_text, (width//2 - title_text.get_width()//2, height//6))
    
    # More spaced-out layout for instructions and input
    instruction_text = multiplayer_small_font.render("Enter Server IP (or press Enter for localhost):", True, white)
    screen.blit(instruction_text, (width//2 - instruction_text.get_width()//2, height//3))
    
    # Display the suggested IP if we found one (move down for spacing)
    y_offset = height//3 + 50
    if suggested_ip:
        suggestion_text = multiplayer_small_font.render(f"Suggested IP: {suggested_ip}", True, (0, 255, 255))
        screen.blit(suggestion_text, (width//2 - suggestion_text.get_width()//2, y_offset))
        y_offset += 50
    else:
        y_offset += 20
    
    # Display connection explanations with more spacing
    connect_text1 = multiplayer_small_font.render("For same computer: use 'localhost'", True, (200, 200, 200))
    screen.blit(connect_text1, (width//2 - connect_text1.get_width()//2, y_offset))
    
    y_offset += 40
    connect_text2 = multiplayer_small_font.render("For different computers: use server's network IP", True, (200, 200, 200))
    screen.blit(connect_text2, (width//2 - connect_text2.get_width()//2, y_offset))
    
    # Move input box further down
    input_rect = pygame.Rect(width//2 - 140, y_offset + 70, 280, 40)
    pygame.draw.rect(screen, white, input_rect)
    
    # Get IP input
    ip_input = ""
    ip_active = True
    pygame.key.set_repeat(500, 50)
    
    while ip_active:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    # If empty, use localhost
                    if ip_input.strip() == "":
                        ip_input = "localhost"
                    ip_active = False
                elif event.key == K_BACKSPACE:
                    ip_input = ip_input[:-1]
                else:
                    # Only allow valid IP characters
                    if event.unicode.isdigit() or event.unicode == '.' or event.unicode.isalpha():
                        ip_input += event.unicode
        
        # Redraw input box
        pygame.draw.rect(screen, white, input_rect)
        text_surface = multiplayer_small_font.render(ip_input, True, black)
        screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
        
        pygame.display.flip()
        clock.tick(30)
    
    server_ip = ip_input
    print(f"Connecting to server: {server_ip}")
    
    # Connection status display
    status_font = multiplayer_small_font
    pygame.draw.rect(screen, black, (0, 0, width, height))
    connecting_text = status_font.render(f"Connecting to {server_ip}...", True, white)
    screen.blit(connecting_text, (width//2 - connecting_text.get_width()//2, height//2))
    connecting_hint = status_font.render("This may take up to 30 seconds...", True, (200, 200, 200))
    screen.blit(connecting_hint, (width//2 - connecting_hint.get_width()//2, height//2 + 40))
    pygame.display.flip()
    
    # Connect to the specified server (with standard port 5555)
    n = Network(server=server_ip)
    player_id = n.player_id
    
    if player_id is None:
        # Display connection error and wait before returning
        error_text = status_font.render("Failed to connect to server.", True, (255, 100, 100))
        hint_text = status_font.render("Check IP address and ensure server is running.", True, (255, 200, 100))
        back_text = status_font.render("Press any key to return to menu...", True, white)
        
        screen.fill(black)
        screen.blit(error_text, (width//2 - error_text.get_width()//2, height//2 - 50))
        screen.blit(hint_text, (width//2 - hint_text.get_width()//2, height//2))
        screen.blit(back_text, (width//2 - back_text.get_width()//2, height//2 + 100))
        pygame.display.flip()
        
        # Wait for keypress before returning
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    waiting = False
        
        return
        
    # Success message
    success_text = status_font.render(f"Connected to server as Player {player_id+1}", True, (100, 255, 100))
    ready_text = status_font.render("Sending ready signal...", True, white)
    screen.fill(black)
    screen.blit(success_text, (width//2 - success_text.get_width()//2, height//2 - 25))
    screen.blit(ready_text, (width//2 - ready_text.get_width()//2, height//2 + 25))
    pygame.display.flip()
    
    print(f"Connected to server as Player {player_id}")
    
    # Tell server we're ready
    game_state = n.send("ready")
    if game_state is None:
        # Display communication error
        error_text = status_font.render("Failed to communicate with server", True, (255, 100, 100))
        back_text = status_font.render("Press any key to return to menu...", True, white)
        
        screen.fill(black)
        screen.blit(error_text, (width//2 - error_text.get_width()//2, height//2))
        screen.blit(back_text, (width//2 - back_text.get_width()//2, height//2 + 100))
        pygame.display.flip()
        
        # Wait for keypress before returning
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    waiting = False
                    
        n.disconnect()
        return
        
    # Waiting for opponent screen
    if game_state.winner == "" and not game_state.game_active:
        waiting_text = status_font.render("Connected! Waiting for opponent...", True, (100, 255, 100))
        screen.fill(black)
        screen.blit(waiting_text, (width//2 - waiting_text.get_width()//2, height//2))
        pygame.display.flip()
    
    # Main game loop for multiplayer
    multiplayer_running = True
    multiplayer_clock = pygame.time.Clock()
    paddle_y = height // 2 - paddle_height // 2  # Initial paddle position
    
    while multiplayer_running:
        # Handle events
        for event in pygame.event.get():
            if event.type == QUIT:
                multiplayer_running = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    multiplayer_running = False
                if event.key == K_r and game_state.winner:  # Restart after game over
                    game_state = n.send("restart")
        
        # Get paddle movement from keyboard
        keys = pygame.key.get_pressed()
        if keys[K_UP]:
            paddle_y -= 7
        if keys[K_DOWN]:
            paddle_y += 7
            
        # Keep paddle within screen bounds
        if paddle_y < 0:
            paddle_y = 0
        if paddle_y > height - paddle_height:
            paddle_y = height - paddle_height
            
        # Send paddle position to server
        game_state = n.send(paddle_y)
        
        if game_state is None:
            print("Lost connection to server")
            break
            
        # Draw everything
        screen.fill(black)
        
        # Draw paddles based on game state
        left_paddle_rect = pygame.Rect(50, game_state.left_paddle_y, 
                                      game_state.paddle_width, game_state.paddle_height)
        right_paddle_rect = pygame.Rect(width - 50 - game_state.paddle_width, 
                                       game_state.right_paddle_y, 
                                       game_state.paddle_width, game_state.paddle_height)
        
        # Highlight the player's paddle
        if player_id == 0:  # Left player
            pygame.draw.rect(screen, (0, 255, 255), left_paddle_rect)  # Cyan for player
            pygame.draw.rect(screen, white, right_paddle_rect)
        else:  # Right player
            pygame.draw.rect(screen, white, left_paddle_rect)
            pygame.draw.rect(screen, (0, 255, 255), right_paddle_rect)  # Cyan for player
            
        # Draw ball
        ball_rect = pygame.Rect(game_state.ball_x, game_state.ball_y, 
                               game_state.ball_size, game_state.ball_size)
        pygame.draw.rect(screen, white, ball_rect)
        
        # Draw scores
        left_text = multiplayer_font.render(str(game_state.left_score), True, white)
        screen.blit(left_text, (width//4, 10))
        right_text = multiplayer_font.render(str(game_state.right_score), True, white)
        screen.blit(right_text, (3*width//4, 10))
        
        # Draw player info
        if player_id == 0:
            player_text = multiplayer_small_font.render("You are Player 1 (Left)", True, (0, 255, 255))
        else:
            player_text = multiplayer_small_font.render("You are Player 2 (Right)", True, (0, 255, 255))
        screen.blit(player_text, (width//2 - player_text.get_width()//2, 10))
        
        # Show game status or winner
        if not game_state.game_active and not game_state.winner:
            waiting_text = multiplayer_small_font.render("Waiting for players to connect...", True, yellow)
            screen.blit(waiting_text, (width//2 - waiting_text.get_width()//2, height//2))
        elif game_state.winner:
            win_text = multiplayer_font.render(game_state.winner, True, white)
            screen.blit(win_text, (width//2 - win_text.get_width()//2, height//2 - 50))
            restart_text = multiplayer_small_font.render("Press R to restart", True, white)
            screen.blit(restart_text, (width//2 - restart_text.get_width()//2, height//2 + 50))
        
        pygame.display.flip()
        multiplayer_clock.tick(60)
    
    # Disconnect from server
    n.disconnect()

# Create difficulty button rectangles
easy_button = pygame.Rect(width//2 - 150, height//2 - 120, 300, 50)
medium_button = pygame.Rect(width//2 - 150, height//2 - 60, 300, 50)
hard_button = pygame.Rect(width//2 - 150, height//2, 300, 50)
practice_button = pygame.Rect(width//2 - 150, height//2 + 60, 300, 50)

# Multiplayer button
multiplayer_button = pygame.Rect(width//2 - 150, height//2 + 120, 300, 50)

# Settings button and sliders
settings_button = pygame.Rect(width//2 - 150, height//2 + 180, 300, 40)
back_button = pygame.Rect(width//2 - 150, height - 100, 300, 40)

# Sliders for physics settings
speed_slider = pygame.Rect(width//2 - 100, height//2 - 80, 200, 20)
speed_handle = pygame.Rect(width//2, height//2 - 80, 20, 20)  # Position will be updated

bounce_slider = pygame.Rect(width//2 - 100, height//2, 200, 20)
bounce_handle = pygame.Rect(width//2, height//2, 20, 20)  # Position will be updated

rebound_slider = pygame.Rect(width//2 - 100, height//2 + 80, 200, 20)
rebound_handle = pygame.Rect(width//2, height//2 + 80, 20, 20)  # Position will be updated

# Toggle button for gravity
gravity_toggle = pygame.Rect(width//2 - 100, height//2 - 150, 200, 30)

# Main game loop
running = True
clock = pygame.time.Clock()
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
            # Toggle pause when P key is pressed, but only if game has started and not over
            if event.key == K_p and game_started and not game_over:
                paused = not paused
            # Return to home screen when H key is pressed
            if event.key == K_h and game_started:
                game_started = False
                game_over = False
                paused = False
                settings_screen = False
                left_score = 0
                right_score = 0
                reset_ball()
                
        # Handle mouse clicks on buttons
        if event.type == MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Main menu buttons
            if not game_started and not settings_screen:
                if easy_button.collidepoint(mouse_pos):
                    difficulty = "easy"
                    ai_speed = 3
                    game_started = True
                    practice_mode = False
                elif medium_button.collidepoint(mouse_pos):
                    difficulty = "medium"
                    ai_speed = 5
                    game_started = True
                    practice_mode = False
                elif hard_button.collidepoint(mouse_pos):
                    difficulty = "hard"
                    ai_speed = 7
                    game_started = True
                    practice_mode = False
                elif practice_button.collidepoint(mouse_pos):
                    difficulty = "medium"
                    ai_speed = 5
                    game_started = True
                    practice_mode = True
                elif multiplayer_button.collidepoint(mouse_pos):
                    # Handle multiplayer mode directly in main.py
                    run_multiplayer_mode()
                elif settings_button.collidepoint(mouse_pos):
                    settings_screen = True
            
            # Settings screen buttons
            elif settings_screen:
                if back_button.collidepoint(mouse_pos):
                    settings_screen = False
                elif gravity_toggle.collidepoint(mouse_pos):
                    gravity_enabled = not gravity_enabled
                    
        # Handle slider dragging
        if event.type == MOUSEBUTTONDOWN and settings_screen:
            mouse_pos = pygame.mouse.get_pos()
            # Check if any slider handle is clicked
            if speed_handle.collidepoint(mouse_pos):
                dragging_speed = True
            elif bounce_handle.collidepoint(mouse_pos):
                dragging_bounce = True
            elif rebound_handle.collidepoint(mouse_pos):
                dragging_rebound = True
                
        if event.type == MOUSEBUTTONUP:
            # Stop dragging
            dragging_speed = False
            dragging_bounce = False
            dragging_rebound = False
            
        # Update slider positions when dragging
        if event.type == MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            if settings_screen:
                if dragging_speed:
                    # Constrain x position to slider bounds
                    new_x = max(speed_slider.left, min(mouse_pos[0], speed_slider.right))
                    speed_handle.centerx = new_x
                    # Calculate ball speed multiplier based on handle position (0.5x to 2.0x)
                    ball_speed_multiplier = 0.5 + ((new_x - speed_slider.left) / speed_slider.width) * 1.5
                
                if dragging_bounce:
                    new_x = max(bounce_slider.left, min(mouse_pos[0], bounce_slider.right))
                    bounce_handle.centerx = new_x
                    # Calculate bounce dampening (0.5 to 1.0)
                    bounce_dampening = 0.5 + ((new_x - bounce_slider.left) / bounce_slider.width) * 0.5
                
                if dragging_rebound:
                    new_x = max(rebound_slider.left, min(mouse_pos[0], rebound_slider.right))
                    rebound_handle.centerx = new_x
                    # Calculate paddle rebound strength (0.5 to 1.5)
                    paddle_rebound_strength = 0.5 + ((new_x - rebound_slider.left) / rebound_slider.width)

    # Display difficulty selection screen
    if not game_started and not settings_screen:
        screen.fill(black)
        title_text = font.render("Select Mode", True, white)
        screen.blit(title_text, (width//2 - title_text.get_width()//2, height//6))  # Moved up from height//4
        
        # Draw buttons
        pygame.draw.rect(screen, green, easy_button)
        easy_text = small_font.render("Easy", True, black)
        screen.blit(easy_text, (easy_button.centerx - easy_text.get_width()//2, easy_button.centery - easy_text.get_height()//2))
        
        pygame.draw.rect(screen, yellow, medium_button)
        medium_text = small_font.render("Medium", True, black)
        screen.blit(medium_text, (medium_button.centerx - medium_text.get_width()//2, medium_button.centery - medium_text.get_height()//2))
        
        pygame.draw.rect(screen, red, hard_button)
        hard_text = small_font.render("Hard", True, black)
        screen.blit(hard_text, (hard_button.centerx - hard_text.get_width()//2, hard_button.centery - hard_text.get_height()//2))
        
        # Practice button
        pygame.draw.rect(screen, (100, 100, 255), practice_button)  # Light blue
        practice_text = small_font.render("Practice Mode", True, black)
        screen.blit(practice_text, (practice_button.centerx - practice_text.get_width()//2, practice_button.centery - practice_text.get_height()//2))
        
        # Multiplayer button
        pygame.draw.rect(screen, (255, 100, 100), multiplayer_button)  # Light red
        multiplayer_text = small_font.render("Multiplayer Mode", True, black)
        screen.blit(multiplayer_text, (multiplayer_button.centerx - multiplayer_text.get_width()//2, multiplayer_button.centery - multiplayer_text.get_height()//2))
        
        # Settings button
        pygame.draw.rect(screen, gray, settings_button)
        settings_text = small_font.render("Ball Physics Settings", True, black)
        screen.blit(settings_text, (settings_button.centerx - settings_text.get_width()//2, settings_button.centery - settings_text.get_height()//2))
        
        instruction_text = small_font.render("Click to select mode", True, white)
        screen.blit(instruction_text, (width//2 - instruction_text.get_width()//2, height - 50))
    
    # Display physics settings screen
    elif settings_screen:
        screen.fill(black)
        title_text = font.render("Ball Physics Settings", True, white)
        screen.blit(title_text, (width//2 - title_text.get_width()//2, height//6))
        
        # Update handle positions based on current settings
        speed_handle.centerx = speed_slider.left + ((ball_speed_multiplier - 0.5) / 1.5) * speed_slider.width
        bounce_handle.centerx = bounce_slider.left + ((bounce_dampening - 0.5) / 0.5) * bounce_slider.width
        rebound_handle.centerx = rebound_slider.left + ((paddle_rebound_strength - 0.5) / 1.0) * rebound_slider.width
        
        # Gravity toggle
        pygame.draw.rect(screen, gray, gravity_toggle)
        gravity_color = green if gravity_enabled else red
        gravity_status = "ON" if gravity_enabled else "OFF"
        gravity_text = small_font.render(f"Gravity: {gravity_status}", True, gravity_color)
        screen.blit(gravity_text, (gravity_toggle.centerx - gravity_text.get_width()//2, gravity_toggle.centery - gravity_text.get_height()//2))
        
        # Ball speed slider
        speed_label = small_font.render(f"Ball Speed: {ball_speed_multiplier:.1f}x", True, white)
        screen.blit(speed_label, (width//2 - speed_label.get_width()//2, speed_slider.top - 30))
        pygame.draw.rect(screen, gray, speed_slider)
        pygame.draw.rect(screen, white, speed_handle)
        
        # Bounce dampening slider
        bounce_label = small_font.render(f"Bounce Energy: {bounce_dampening:.2f}", True, white)
        screen.blit(bounce_label, (width//2 - bounce_label.get_width()//2, bounce_slider.top - 30))
        pygame.draw.rect(screen, gray, bounce_slider)
        pygame.draw.rect(screen, white, bounce_handle)
        
        # Paddle rebound strength slider
        rebound_label = small_font.render(f"Paddle Power: {paddle_rebound_strength:.2f}", True, white)
        screen.blit(rebound_label, (width//2 - rebound_label.get_width()//2, rebound_slider.top - 30))
        pygame.draw.rect(screen, gray, rebound_slider)
        pygame.draw.rect(screen, white, rebound_handle)
        
        # Back button
        pygame.draw.rect(screen, gray, back_button)
        back_text = small_font.render("Back to Main Menu", True, black)
        screen.blit(back_text, (back_button.centerx - back_text.get_width()//2, back_button.centery - back_text.get_height()//2))
        
    # Game logic (only executes if game is started, not over, and not paused)
    elif not game_over and not paused:
        # Additional controls for practice mode
        if practice_mode:
            keys = pygame.key.get_pressed()
            # Reset ball position with spacebar
            if keys[K_SPACE]:
                reset_ball()
            # Adjust ball speed with additional keys in practice mode
            if keys[K_w]:  # Increase vertical speed up
                ball_speed_y -= 0.2
            if keys[K_s]:  # Increase vertical speed down
                ball_speed_y += 0.2
            if keys[K_a]:  # Decrease horizontal speed
                if ball_speed_x > 0:
                    ball_speed_x -= 0.2
                else:
                    ball_speed_x += 0.2
            if keys[K_d]:  # Increase horizontal speed
                if ball_speed_x > 0:
                    ball_speed_x += 0.2
                else:
                    ball_speed_x -= 0.2
        # AI difficulty affects paddle speed
        # For easy, the AI will sometimes make mistakes
        if difficulty == "easy":
            # 15% chance AI will move randomly
            if random.random() < 0.15:
                left_paddle.y += random.choice([-3, 3])
            else:
                # Move left paddle to align with ball, but slower
                desired_y = ball.centery - paddle_height // 2
                if left_paddle.y < desired_y:
                    left_paddle.y += ai_speed
                elif left_paddle.y > desired_y:
                    left_paddle.y -= ai_speed
        
        # Medium AI follows the ball but not perfectly
        elif difficulty == "medium":
            # Add slight delay/lag to medium difficulty
            desired_y = ball.centery - paddle_height // 2
            if left_paddle.y < desired_y - 10:
                left_paddle.y += ai_speed
            elif left_paddle.y > desired_y + 10:
                left_paddle.y -= ai_speed
        
        # Hard AI predicts the ball's movement
        elif difficulty == "hard":
            # Perfect tracking and attempt to predict future ball position
            # Calculate ball's future position when it reaches paddle's x position
            if ball_speed_x < 0:  # Only predict when ball is moving toward AI
                time_to_hit = (left_paddle.right - ball.left) / abs(ball_speed_x)
                future_y = ball.centery + (ball_speed_y * time_to_hit)
                
                # If ball will hit top or bottom, adjust prediction
                # Simple bounce prediction
                while future_y < 0 or future_y > height:
                    if future_y < 0:
                        future_y = -future_y
                    elif future_y > height:
                        future_y = 2 * height - future_y
                
                desired_y = future_y - paddle_height // 2
            else:
                # When ball is moving away, return to center position
                desired_y = height // 2 - paddle_height // 2
                
            if left_paddle.y < desired_y:
                left_paddle.y += ai_speed
            elif left_paddle.y > desired_y:
                left_paddle.y -= ai_speed

        # Player controls for right paddle
        keys = pygame.key.get_pressed()
        if keys[K_UP]:
            right_paddle.y -= 7  # Player speed fixed at 7
        if keys[K_DOWN]:
            right_paddle.y += 7

        # Clamp paddles to stay within screen bounds
        left_paddle.clamp_ip(screen.get_rect())
        right_paddle.clamp_ip(screen.get_rect())

        # Move ball
        ball.x += ball_speed_x
        ball.y += ball_speed_y

        # Apply gravity if enabled
        if gravity_enabled:
            ball_speed_y += 0.2  # Constant downward acceleration
            
        # Ball collision with top and bottom walls
        if ball.top <= 0:
            ball.top = 0
            ball_speed_y = -ball_speed_y * bounce_dampening
        elif ball.bottom >= height:
            ball.bottom = height
            ball_speed_y = -ball_speed_y * bounce_dampening
            
        # Ball collision with paddles
        if ball.colliderect(left_paddle):
            hit_pos = (ball.centery - left_paddle.centery) / (paddle_height / 2)
            # Adjust vertical speed based on hit position and rebound strength
            ball_speed_y = hit_pos * 5 * paddle_rebound_strength
            # Bounce horizontally with dampening
            ball_speed_x = -ball_speed_x * bounce_dampening
            # Ensure ball doesn't get stuck in paddle
            ball.left = left_paddle.right + 1
            
            # Increase speed slightly on hit for more challenge as game progresses
            if ball_speed_x > 0:
                ball_speed_x += 0.2 * ball_speed_multiplier
            else:
                ball_speed_x -= 0.2 * ball_speed_multiplier
                
        elif ball.colliderect(right_paddle):
            hit_pos = (ball.centery - right_paddle.centery) / (paddle_height / 2)
            # Adjust vertical speed based on hit position and rebound strength
            ball_speed_y = hit_pos * 5 * paddle_rebound_strength
            # Bounce horizontally with dampening
            ball_speed_x = -ball_speed_x * bounce_dampening
            # Ensure ball doesn't get stuck in paddle
            ball.right = right_paddle.left - 1
            
            # Increase speed slightly on hit
            if ball_speed_x > 0:
                ball_speed_x += 0.2 * ball_speed_multiplier
            else:
                ball_speed_x -= 0.2 * ball_speed_multiplier

        # Scoring and win condition
        if not practice_mode:
            if ball.left <= 0:
                right_score += 1
                reset_ball()
            elif ball.right >= width:
                left_score += 1
                reset_ball()

            # **Check if someone scores over 30 points**
            if left_score > 7:
                winner = "Computer Wins!"
                game_over = True
            elif right_score > 7:
                winner = "Player Wins!"
                game_over = True
        else:
            # Practice mode - just reset the ball when it goes out, no scoring
            if ball.left <= 0 or ball.right >= width:
                reset_ball()

        # Draw everything
        screen.fill(black)
        
        # Draw game elements
        pygame.draw.rect(screen, white, left_paddle)
        pygame.draw.rect(screen, white, right_paddle)
        pygame.draw.rect(screen, white, ball)
        
        # Draw scores
        left_text = font.render(str(left_score), True, white)
        screen.blit(left_text, (width//4, 10))
        right_text = font.render(str(right_score), True, white)
        screen.blit(right_text, (3*width//4, 10))
        
        # Draw difficulty indicator
        diff_color = green if difficulty == "easy" else yellow if difficulty == "medium" else red
        diff_text = small_font.render(f"Difficulty: {difficulty.capitalize()}", True, diff_color)
        screen.blit(diff_text, (width//2 - diff_text.get_width()//2, 10))
        
        # Display control hints
        pause_hint = small_font.render("Press P to pause | H for Home", True, gray)
        screen.blit(pause_hint, (width//2 - pause_hint.get_width()//2, height - 30))
        
        # Additional instructions for practice mode
        if practice_mode:
            controls_text = small_font.render("SPACE: Reset Ball | W/S: Adjust Vertical | A/D: Adjust Horizontal", True, gray)
            screen.blit(controls_text, (width//2 - controls_text.get_width()//2, height - 60))
        
    # Pause screen
    elif paused and game_started and not game_over:
        # Create semi-transparent overlay
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Black with alpha
        screen.blit(overlay, (0, 0))
        
        # Draw pause text
        pause_text = font.render("PAUSED", True, white)
        screen.blit(pause_text, (width//2 - pause_text.get_width()//2, height//2 - pause_text.get_height()//2))
        
        # Draw controls reminder
        resume_text = small_font.render("Press P to resume", True, white)
        screen.blit(resume_text, (width//2 - resume_text.get_width()//2, height//2 + 50))
        
        home_text = small_font.render("Press H for home screen", True, white)
        screen.blit(home_text, (width//2 - home_text.get_width()//2, height//2 + 90))
        
        quit_text = small_font.render("Press ESC to quit", True, white)
        screen.blit(quit_text, (width//2 - quit_text.get_width()//2, height//2 + 130))
    
    elif game_over:
        # Draw win message centered on screen
        screen.fill(black)
        win_text = font.render(winner, True, white)
        screen.blit(win_text, (width//2 - win_text.get_width()//2, height//2 - win_text.get_height()//2))
        
        # Draw difficulty info
        diff_color = green if difficulty == "easy" else yellow if difficulty == "medium" else red
        diff_text = small_font.render(f"Difficulty: {difficulty.capitalize()}", True, diff_color)
        screen.blit(diff_text, (width//2 - diff_text.get_width()//2, height//2 + 50))
        
        # Home screen option
        home_text = small_font.render("Press H to return to home screen", True, white)
        screen.blit(home_text, (width//2 - home_text.get_width()//2, height//2 + 100))

    pygame.display.flip()
    clock.tick(60)

# Quit Pygame
pygame.quit()