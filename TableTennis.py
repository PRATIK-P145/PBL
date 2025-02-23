import pygame

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Touchless Table Tennis")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Paddle & Ball
paddle = pygame.Rect(WIDTH // 2 - 60, HEIGHT - 30, 120, 10)
ball = pygame.Rect(WIDTH // 2 - 10, HEIGHT // 2 - 10, 20, 20)
ball_dx, ball_dy = 5, -5

# Game Loop
running = True
while running:
    screen.fill(BLACK)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    pygame.draw.rect(screen, WHITE, paddle)
    pygame.draw.ellipse(screen, WHITE, ball)

    # Ball movement
    ball.x += ball_dx
    ball.y += ball_dy

    # Ball collision with walls
    if ball.left <= 0 or ball.right >= WIDTH:
        ball_dx *= -1
    if ball.top <= 0:
        ball_dy *= -1

    # Ball collision with paddle
    if ball.colliderect(paddle):
        ball_dy *= -1

    pygame.display.flip()
    pygame.time.delay(30)

pygame.quit()
