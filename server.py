import socket
import pickle
import threading
import random
import time
import os
import traceback
import platform

# Enable debug logging
DEBUG_MODE = True
DEBUG_LOG_PATH = os.path.join(os.path.dirname(__file__), "server_debug.log")

def log(message):
    """Log a message to both console and log file"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {message}"
    print(formatted)
    
    if DEBUG_MODE:
        try:
            with open(DEBUG_LOG_PATH, "a") as f:
                f.write(formatted + "\n")
        except:
            pass  # If logging fails, continue anyway

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
        # Clear any existing log file
        if DEBUG_MODE:
            try:
                with open(DEBUG_LOG_PATH, "w") as f:
                    f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Server debug log started\n")
                    f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Platform: {platform.platform()}\n")
                    f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Python version: {platform.python_version()}\n")
            except Exception as e:
                print(f"Failed to initialize log file: {e}")
    
        log(f"Initializing server with host='{host}', port={port}")
        
        # Create socket with IPv4 addressing and TCP
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Set timeout to prevent blocking indefinitely
        self.server.settimeout(600)  # 10 minutes timeout
        
        self.host = host
        self.port = port
        
        try:
            self.server.bind((self.host, self.port))
            log(f"Socket successfully bound to {self.host if self.host else '*'}:{self.port}")
        except socket.error as e:
            log(f"CRITICAL ERROR: Socket binding failed: {e}")
            log(traceback.format_exc())
            raise  # Re-raise the exception to stop execution
            
        self.server.listen(2)
        log(f"Server listening on port {self.port}, waiting for connections...")
        
        self.connections = {}
        self.players_ready = set()
        self.game_state = GameState()
        self.game_thread = None
        self.game_running = False

    def handle_client(self, conn, player_id):
        log(f"New client handler started for Player {player_id}")
        
        # Set connection timeout to prevent blocking indefinitely
        conn.settimeout(30)  # 30 second timeout
        
        # Send initial player ID
        try:
            player_id_data = pickle.dumps(player_id)
            log(f"Sending player_id={player_id} to client ({len(player_id_data)} bytes)")
            conn.send(player_id_data)
        except Exception as e:
            log(f"ERROR: Failed to send initial player ID to client: {e}")
            log(traceback.format_exc())
            return
        
        log(f"Player {player_id} initialized successfully")
        
        try:
            while True:
                try:
                    # Receive paddle position from client
                    log(f"Waiting for data from Player {player_id}...")
                    data = conn.recv(2048)
                    
                    if not data:  # Connection closed
                        log(f"No data received from Player {player_id} - connection closed")
                        break
                    
                    log(f"Received {len(data)} bytes from Player {player_id}")    
                    
                    try:
                        data = pickle.loads(data)
                        log(f"Player {player_id} sent: {data}")
                    except Exception as e:
                        log(f"ERROR: Failed to unpickle data from Player {player_id}: {e}")
                        log(f"First 100 bytes of raw data: {data[:100]}")
                        continue
                    
                    if data == "ready":
                        log(f"Player {player_id} is ready")
                        self.players_ready.add(player_id)
                        log(f"Ready players: {self.players_ready}")
                        # If both players are ready, start the game
                        if len(self.players_ready) == 2 and not self.game_running:
                            log("Both players ready! Starting game...")
                            self.start_game_thread()
                    
                    elif data == "restart":
                        log(f"Player {player_id} requested game restart")
                        self.game_state.start_game()
                    
                    elif data is not None:  # Regular paddle update
                        # Update paddle position based on player
                        if player_id == 0:  # Player 1 (left paddle)
                            self.game_state.left_paddle_y = data
                        else:  # Player 2 (right paddle)
                            self.game_state.right_paddle_y = data
                    
                    # Send current game state to the client
                    try:
                        game_state_data = pickle.dumps(self.game_state)
                        log(f"Sending game state to Player {player_id} ({len(game_state_data)} bytes)")
                        conn.send(game_state_data)
                    except Exception as e:
                        log(f"ERROR: Failed to send game state to Player {player_id}: {e}")
                        break
                    
                except socket.timeout:
                    log(f"WARNING: Connection with Player {player_id} timed out waiting for data")
                    # Don't break - just continue and try again
                    continue
                except ConnectionResetError:
                    log(f"ERROR: Connection reset by Player {player_id}")
                    break
                except Exception as e:
                    log(f"ERROR: Unexpected error in client handler for Player {player_id}: {e}")
                    log(traceback.format_exc())
                    break
                    
        finally:
            log(f"Player {player_id} disconnected - cleaning up resources")
            if player_id in self.players_ready:
                self.players_ready.remove(player_id)
                log(f"Removed Player {player_id} from ready players")
            
            if player_id in self.connections and self.connections[player_id] == conn:
                del self.connections[player_id]
                log(f"Removed Player {player_id} from active connections")
            
            try:
                conn.close()
                log(f"Closed socket connection for Player {player_id}")
            except Exception as e:
                log(f"ERROR: Failed to close connection for Player {player_id}: {e}")
                pass
            
    def start_game_thread(self):
        log("Starting game thread - setting game_active to True")
        self.game_running = True
        self.game_state.start_game()
        log(f"Game state is now: active={self.game_state.game_active}, ball_pos=({self.game_state.ball_x}, {self.game_state.ball_y})")
        
        try:
            self.game_thread = threading.Thread(target=self.game_loop)
            self.game_thread.daemon = True
            self.game_thread.start()
            log("Game thread started successfully")
        except Exception as e:
            log(f"ERROR: Failed to start game thread: {e}")
            log(traceback.format_exc())
            self.game_running = False
        
    def game_loop(self):
        log("Game loop started")
        last_time = time.time()
        loop_count = 0
        
        try:
            while self.game_running:
                loop_count += 1
                if loop_count % 60 == 0:  # Log every second (assuming 60 FPS)
                    log(f"Game loop running. Ball position: ({self.game_state.ball_x}, {self.game_state.ball_y})")
                
                # Check if we have two players connected
                if len(self.connections) < 2:
                    log("Game paused: waiting for two players")
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
                    log("Game is no longer active - ending game loop")
                    self.game_running = False
                    
        except Exception as e:
            log(f"ERROR: Unexpected error in game loop: {e}")
            log(traceback.format_exc())
            self.game_running = False
        
        log("Game loop ended - clearing ready players")
        self.players_ready.clear()
        
    def start(self):
        current_player = 0
        
        log(f"Server starting main accept loop on port {self.port}")
        
        while True:
            try:
                # Wait for a new connection
                log("Waiting for a new connection...")
                conn, addr = self.server.accept()
                log(f"New connection from: {addr}")
                
                # Set socket options for better reliability
                try:
                    # Set TCP keepalive
                    conn.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                    
                    # Set timeout to prevent blocking indefinitely
                    conn.settimeout(30)
                    log(f"Socket options set for connection from {addr}")
                except Exception as e:
                    log(f"WARNING: Could not set socket options: {e}")
                
                # Only accept two players
                if len(self.connections) < 2:
                    # If player ID is already in use, find an available ID
                    if current_player in self.connections:
                        log(f"Player ID {current_player} already in use, switching to the other ID")
                        current_player = 0 if current_player == 1 else 1
                    
                    # Store connection and start client handler thread
                    log(f"Assigning player ID {current_player} to connection from {addr}")
                    self.connections[current_player] = conn
                    
                    # Create and start a new thread to handle this client
                    client_thread = threading.Thread(
                        target=self.handle_client, 
                        args=(conn, current_player),
                        name=f"Player-{current_player}-Handler"
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    log(f"Started handler thread for Player {current_player}")
                    
                    # Prepare for next connection
                    current_player = (current_player + 1) % 2
                else:
                    log(f"Rejected connection from {addr}: server full (2 players already connected)")
                    try:
                        # Send a friendly rejection message before closing
                        rejection_msg = pickle.dumps("SERVER_FULL")
                        conn.send(rejection_msg)
                    except:
                        pass  # Ignore errors in sending rejection
                    finally:
                        conn.close()
                        log(f"Closed rejected connection from {addr}")
            
            except socket.timeout:
                log("Accept timed out - continuing to accept loop")
                continue
            except Exception as e:
                log(f"ERROR: Unexpected error in accept loop: {e}")
                log(traceback.format_exc())
                # Sleep briefly to avoid tight loop in case of persistent errors
                time.sleep(1)

if __name__ == "__main__":
    # Get host's IP address to display for clients
    try:
        log("Starting server - detecting network interfaces...")
        
        # Always clear firewall warning
        log("\n" + "="*80)
        log("IMPORTANT: Make sure your firewall allows incoming connections on port 5555")
        log("If clients can't connect, you may need to add a firewall exception")
        log("="*80 + "\n")
        
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        log(f"Simple hostname resolution: {local_ip}")
        
        log("\nALL AVAILABLE NETWORK INTERFACES:")
        
        # Track all IPs for a summary
        all_detected_ips = []
        
        # Try the netifaces method first (most reliable)
        try:
            import netifaces
            
            log("Network interfaces detected:")
            for interface in netifaces.interfaces():
                addresses = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addresses:
                    for link in addresses[netifaces.AF_INET]:
                        ip = link['addr']
                        if not ip.startswith('127.'):  # Skip localhost
                            all_detected_ips.append(ip)
                        log(f"  {interface}: {ip}")
        
        except ImportError:
            log("netifaces module not installed. Using alternative method.")
            
            # Fallback method using socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                # Doesn't need to be reachable, just used to get local interface address
                s.connect(('10.255.255.255', 1))
                ip = s.getsockname()[0]
                if not ip.startswith('127.'):  # Skip localhost
                    all_detected_ips.append(ip) 
                log(f"  Primary IP: {ip}")
            except Exception as e:
                log(f"  Socket method failed: {e}")
            finally:
                s.close()
                
        # Try socket.getaddrinfo as well
        try:
            host_info = socket.getaddrinfo(
                socket.gethostname(), None, socket.AF_INET, socket.SOCK_STREAM
            )
            for ip in set([x[4][0] for x in host_info]):
                if ip not in all_detected_ips and not ip.startswith('127.'):
                    all_detected_ips.append(ip)
                    log(f"  Additional IP from getaddrinfo: {ip}")
        except Exception as e:
            log(f"getaddrinfo method failed: {e}")
        
        # Display clear connection instructions
        log("\n" + "="*80)
        if all_detected_ips:
            log("CONNECTION INSTRUCTIONS:")
            log("For clients on the same computer: Use 'localhost'")
            log("For clients on your network, try these IP addresses:")
            for i, ip in enumerate(all_detected_ips):
                log(f"  {i+1}. {ip}")
            
            # Pick the most likely candidate
            best_ip = all_detected_ips[0]
            log(f"\nRECOMMENDED CONNECTION ADDRESS: {best_ip}")
        else:
            log("WARNING: Could not determine any network IP addresses")
            log("Clients on the same computer can use 'localhost'")
            log("For network connections, use 'ipconfig' or 'ifconfig' to find your IP")
        log("="*80)
        
    except Exception as e:
        log(f"ERROR: Could not determine network interfaces: {e}")
        log(traceback.format_exc())
    
    # Start the server
    try:
        log("\nInitializing game server...")
        server = Server()
        log("Server initialized, starting accept loop...")
        server.start()
    except Exception as e:
        log(f"CRITICAL ERROR: Server failed to start: {e}")
        log(traceback.format_exc())
        input("Press Enter to exit...")