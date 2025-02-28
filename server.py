import socket
import pickle
import threading
import random
import time

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
                    data = pickle.loads(conn.recv(2048))
                    
                    if data == "ready":
                        self.players_ready.add(player_id)
                        # If both players are ready, start the game
                        if len(self.players_ready) == 2 and not self.game_running:
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
                    
                except Exception as e:
                    print(f"Error in client handler: {e}")
                    break
                    
        finally:
            print(f"Player {player_id} disconnected")
            if player_id in self.players_ready:
                self.players_ready.remove(player_id)
            if player_id in self.connections:
                del self.connections[player_id]
            conn.close()
            
    def start_game_thread(self):
        self.game_running = True
        self.game_state.start_game()
        self.game_thread = threading.Thread(target=self.game_loop)
        self.game_thread.daemon = True
        self.game_thread.start()
        
    def game_loop(self):
        last_time = time.time()
        
        while self.game_running and len(self.connections) == 2:
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
            if current_player <= 1:
                # Store connection and start client handler thread
                self.connections[current_player] = conn
                threading.Thread(target=self.handle_client, args=(conn, current_player)).start()
                current_player = (current_player + 1) % 2
            else:
                conn.close()

if __name__ == "__main__":
    server = Server()
    server.start()