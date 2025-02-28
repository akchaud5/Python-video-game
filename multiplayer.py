import pygame
from pygame.locals import *
import sys
from network import Network

# Initialize Pygame
pygame.init()

# Set up the screen
width = 800
height = 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Ping Pong Multiplayer")

# Define colors
black = (0, 0, 0)
white = (255, 255, 255)
gray = (150, 150, 150)
green = (0, 255, 0)
red = (255, 0, 0)
blue = (0, 0, 255)

# Set up font for text rendering
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)
tiny_font = pygame.font.Font(None, 24)

# Define paddle dimensions
paddle_width = 20
paddle_height = 100

# Game state variables
connecting = True
waiting_for_opponent = False
game_active = False
connection_error = False
player_id = None

def draw_connection_screen():
    screen.fill(black)
    text = font.render("Connecting to server...", True, white)
    screen.blit(text, (width//2 - text.get_width()//2, height//2 - text.get_height()//2))
    
    if connection_error:
        error_text = small_font.render("Connection failed. Press R to retry or ESC to exit.", True, red)
        screen.blit(error_text, (width//2 - error_text.get_width()//2, height//2 + 50))

def draw_waiting_screen():
    screen.fill(black)
    text = font.render("Waiting for opponent...", True, white)
    screen.blit(text, (width//2 - text.get_width()//2, height//2 - text.get_height()//2))
    
    ready_text = small_font.render("Press SPACE when ready", True, green)
    screen.blit(ready_text, (width//2 - ready_text.get_width()//2, height//2 + 50))

def draw_game(game_state, player_id):
    # Clear screen
    screen.fill(black)
    
    # Draw paddles
    left_paddle = pygame.Rect(50, game_state.left_paddle_y, paddle_width, paddle_height)
    right_paddle = pygame.Rect(width - 50 - paddle_width, game_state.right_paddle_y, paddle_width, paddle_height)
    
    # Highlight player's paddle
    if player_id == 0:  # Player 1 (left)
        pygame.draw.rect(screen, blue, left_paddle)
        pygame.draw.rect(screen, white, right_paddle)
    else:  # Player 2 (right)
        pygame.draw.rect(screen, white, left_paddle)
        pygame.draw.rect(screen, blue, right_paddle)
    
    # Draw ball
    ball = pygame.Rect(game_state.ball_x, game_state.ball_y, game_state.ball_size, game_state.ball_size)
    pygame.draw.rect(screen, white, ball)
    
    # Draw scores
    left_text = font.render(str(game_state.left_score), True, white)
    screen.blit(left_text, (width//4, 10))
    right_text = font.render(str(game_state.right_score), True, white)
    screen.blit(right_text, (3*width//4, 10))
    
    # Draw player labels
    p1_text = small_font.render("Player 1", True, white)
    screen.blit(p1_text, (width//4 - p1_text.get_width()//2, 60))
    p2_text = small_font.render("Player 2", True, white)
    screen.blit(p2_text, (3*width//4 - p2_text.get_width()//2, 60))
    
    # Draw game status if not active
    if not game_state.game_active and game_state.winner:
        # Create semi-transparent overlay
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Black with alpha
        screen.blit(overlay, (0, 0))
        
        # Draw winner message
        win_text = font.render(game_state.winner, True, white)
        screen.blit(win_text, (width//2 - win_text.get_width()//2, height//2 - win_text.get_height()//2))
        
        # Draw restart instruction
        restart_text = small_font.render("Press R to restart", True, white)
        screen.blit(restart_text, (width//2 - restart_text.get_width()//2, height//2 + 50))
    
    # Draw network info at bottom
    net_text = tiny_font.render(f"You are Player {player_id+1}", True, gray)
    screen.blit(net_text, (10, height - 20))

def main():
    global connecting, waiting_for_opponent, game_active, connection_error, player_id
    
    # Try to connect to server
    network = Network()
    
    if network.player_id is None:
        connection_error = True
    else:
        player_id = network.player_id
        connecting = False
        waiting_for_opponent = True
    
    # Main game loop
    clock = pygame.time.Clock()
    running = True
    ready_sent = False
    restart_sent = False
    
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                    
                # Handle reconnection
                if connection_error and event.key == K_r:
                    connecting = True
                    connection_error = False
                    network = Network()
                    
                    if network.player_id is None:
                        connection_error = True
                    else:
                        player_id = network.player_id
                        connecting = False
                        waiting_for_opponent = True
                        
                # Handle ready state
                if waiting_for_opponent and event.key == K_SPACE and not ready_sent:
                    network.send("ready")
                    ready_sent = True
                    
                # Handle restart
                if not game_active and event.key == K_r and not restart_sent:
                    network.send("restart")
                    restart_sent = True
        
        # Draw appropriate screen based on game state
        if connecting:
            draw_connection_screen()
        elif waiting_for_opponent:
            draw_waiting_screen()
        else:
            # Get current paddle position based on player
            keys = pygame.key.get_pressed()
            paddle_y = None
            
            if player_id == 0:  # Left paddle (Player 1)
                paddle_y = network.game_state.left_paddle_y
                if keys[K_w] and paddle_y > 0:
                    paddle_y -= 7
                if keys[K_s] and paddle_y < height - paddle_height:
                    paddle_y += 7
            else:  # Right paddle (Player 2)
                paddle_y = network.game_state.right_paddle_y
                if keys[K_UP] and paddle_y > 0:
                    paddle_y -= 7
                if keys[K_DOWN] and paddle_y < height - paddle_height:
                    paddle_y += 7
                    
            # Send paddle position to server and get game state
            game_state = network.send(paddle_y)
            
            if game_state:
                # Update local game state
                network.game_state = game_state
                game_active = game_state.game_active
                
                # If game was inactive but is now active, update waiting status
                if not waiting_for_opponent and not game_active and not game_state.winner:
                    waiting_for_opponent = True
                    ready_sent = False
                elif waiting_for_opponent and game_active:
                    waiting_for_opponent = False
                    
                # If game was over and restarted
                if not game_active and game_state.game_active:
                    game_active = True
                    restart_sent = False
                
                # Draw game state
                draw_game(game_state, player_id)
            else:
                # Connection lost
                connection_error = True
                connecting = True
                
        pygame.display.flip()
        clock.tick(60)
    
    # Cleanup
    if network:
        network.disconnect()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()