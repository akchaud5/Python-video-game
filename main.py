import pygame
from pygame.locals import *
import random

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

# Create paddles
paddle_width = 20
paddle_height = 100
left_paddle = pygame.Rect(50, height//2 - paddle_height//2, paddle_width, paddle_height)
right_paddle = pygame.Rect(width - 50 - paddle_width, height//2 - paddle_height//2, paddle_width, paddle_height)

# Create ball
ball_size = 20
ball = pygame.Rect(width//2 - ball_size//2, height//2 - ball_size//2, ball_size, ball_size)

# Set initial ball speed
ball_speed_x = 5 * random.choice([-1, 1])
ball_speed_y = random.randint(-5, 5)

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
difficulty = "medium"  # Default difficulty
ai_speed = 5  # Default AI speed for medium difficulty

# Function to reset the ball to the center
def reset_ball():
    global ball_speed_x, ball_speed_y
    ball.center = (width//2, height//2)
    ball_speed_x = 5 * random.choice([-1, 1])
    ball_speed_y = random.randint(-5, 5)

# Create difficulty button rectangles
easy_button = pygame.Rect(width//2 - 150, height//2 - 60, 300, 50)
medium_button = pygame.Rect(width//2 - 150, height//2, 300, 50)
hard_button = pygame.Rect(width//2 - 150, height//2 + 60, 300, 50)

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
                
        # Handle mouse clicks on difficulty buttons
        if event.type == MOUSEBUTTONDOWN and not game_started:
            mouse_pos = pygame.mouse.get_pos()
            
            if easy_button.collidepoint(mouse_pos):
                difficulty = "easy"
                ai_speed = 3
                game_started = True
            elif medium_button.collidepoint(mouse_pos):
                difficulty = "medium"
                ai_speed = 5
                game_started = True
            elif hard_button.collidepoint(mouse_pos):
                difficulty = "hard"
                ai_speed = 7
                game_started = True

    # Display difficulty selection screen
    if not game_started:
        screen.fill(black)
        title_text = font.render("Select Difficulty", True, white)
        screen.blit(title_text, (width//2 - title_text.get_width()//2, height//4))
        
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
        
        instruction_text = small_font.render("Click to select difficulty", True, white)
        screen.blit(instruction_text, (width//2 - instruction_text.get_width()//2, height - 100))
        
    # Game logic (only executes if game is started, not over, and not paused)
    elif not game_over and not paused:
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

        # Ball collision with top and bottom walls
        if ball.top <= 0 or ball.bottom >= height:
            ball_speed_y = -ball_speed_y

        # Ball collision with paddles
        if ball.colliderect(left_paddle):
            hit_pos = (ball.centery - left_paddle.centery) / (paddle_height / 2)
            ball_speed_y = hit_pos * 5  # Adjust vertical speed based on hit position
            ball_speed_x = -ball_speed_x  # Bounce horizontally
            # Increase speed slightly on hit for more challenge as game progresses
            if ball_speed_x > 0:
                ball_speed_x += 0.2
            else:
                ball_speed_x -= 0.2
        elif ball.colliderect(right_paddle):
            hit_pos = (ball.centery - right_paddle.centery) / (paddle_height / 2)
            ball_speed_y = hit_pos * 5
            ball_speed_x = -ball_speed_x
            # Increase speed slightly on hit
            if ball_speed_x > 0:
                ball_speed_x += 0.2
            else:
                ball_speed_x -= 0.2

        # Scoring and win condition
        if ball.left <= 0:
            right_score += 1
            reset_ball()
        elif ball.right >= width:
            left_score += 1
            reset_ball()

        # **Check if someone scores over 30 points**
        if left_score > 10:
            winner = "Computer Wins!"
            game_over = True
        elif right_score > 10:
            winner = "Player Wins!"
            game_over = True

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
        
        # Display pause hint
        pause_hint = small_font.render("Press P to pause", True, gray)
        screen.blit(pause_hint, (width//2 - pause_hint.get_width()//2, height - 30))
        
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
        
        quit_text = small_font.render("Press ESC to quit", True, white)
        screen.blit(quit_text, (width//2 - quit_text.get_width()//2, height//2 + 90))
    
    elif game_over:
        # Draw win message centered on screen
        screen.fill(black)
        win_text = font.render(winner, True, white)
        screen.blit(win_text, (width//2 - win_text.get_width()//2, height//2 - win_text.get_height()//2))
        
        # Draw difficulty info
        diff_color = green if difficulty == "easy" else yellow if difficulty == "medium" else red
        diff_text = small_font.render(f"Difficulty: {difficulty.capitalize()}", True, diff_color)
        screen.blit(diff_text, (width//2 - diff_text.get_width()//2, height//2 + 50))

    pygame.display.flip()
    clock.tick(60)

# Quit Pygame
pygame.quit()