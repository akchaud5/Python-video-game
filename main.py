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

# Game state variables
game_over = False
winner = ""

# Function to reset the ball to the center
def reset_ball():
    global ball_speed_x, ball_speed_y
    ball.center = (width//2, height//2)
    ball_speed_x = 5 * random.choice([-1, 1])
    ball_speed_y = random.randint(-5, 5)

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

    # Game logic (only executes if game is not over)
    if not game_over:
        # **Automate the left paddle**
        # Move left paddle to align its center with the ball's center
        desired_y = ball.centery - paddle_height // 2
        if left_paddle.y < desired_y:
            left_paddle.y += 5  # Move down
        elif left_paddle.y > desired_y:
            left_paddle.y -= 5  # Move up

        # Player controls for right paddle
        keys = pygame.key.get_pressed()
        if keys[K_UP]:
            right_paddle.y -= 5
        if keys[K_DOWN]:
            right_paddle.y += 5

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
        elif ball.colliderect(right_paddle):
            hit_pos = (ball.centery - right_paddle.centery) / (paddle_height / 2)
            ball_speed_y = hit_pos * 5
            ball_speed_x = -ball_speed_x

        # Scoring and win condition
        if ball.left <= 0:
            right_score += 1
            reset_ball()
        elif ball.right >= width:
            left_score += 1
            reset_ball()

        # **Check if someone scores over 30 points**
        if left_score > 30:
            winner = "Computer Wins!"
            game_over = True
        elif right_score > 30:
            winner = "Player Wins!"
            game_over = True

    # Draw everything
    screen.fill(black)
    if not game_over:
        # Draw game elements
        pygame.draw.rect(screen, white, left_paddle)
        pygame.draw.rect(screen, white, right_paddle)
        pygame.draw.rect(screen, white, ball)
        # Draw scores
        left_text = font.render(str(left_score), True, white)
        screen.blit(left_text, (width//4, 10))
        right_text = font.render(str(right_score), True, white)
        screen.blit(right_text, (3*width//4, 10))
    else:
        # Draw win message centered on screen
        win_text = font.render(winner, True, white)
        screen.blit(win_text, (width//2 - win_text.get_width()//2, height//2 - win_text.get_height()//2))

    pygame.display.flip()
    clock.tick(60)

# Quit Pygame
pygame.quit()