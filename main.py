import pygame
import sys

# 1. Initialize Pygame
pygame.init()

# 2. Setup the Screen
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 360
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("My Blasphemous Project")

# 3. Setup the Game Clock
clock = pygame.time.Clock()
FPS = 60

# --- PLAYER PROPERTIES ---
# Create a rectangle at X=300, Y=200, with a Width=32 and Height=64 (knight proportions)
player_rect = pygame.Rect(300, 200, 32, 64)
player_speed = 4  # How many pixels the player moves per frame

# --- THE GAME LOOP ---
running = True
while running:
    # --- PHASE 1: GET INPUT ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get a dictionary of all keyboard keys currently being held down
    keys = pygame.key.get_pressed()

    # --- PHASE 2: UPDATE LOGIC ---
    # Move left
    if keys[pygame.K_LEFT]:
        player_rect.x -= player_speed
    # Move right
    if keys[pygame.K_RIGHT]:
        player_rect.x += player_speed

    # Screen boundaries (Keep the player inside the window)
    if player_rect.left < 0:
        player_rect.left = 0
    if player_rect.right > SCREEN_WIDTH:
        player_rect.right = SCREEN_WIDTH

    # --- PHASE 3: RENDER (DRAW) ---
    screen.fill((40, 30, 45))  # Clear screen with dark purple

    # Draw our player rectangle onto the screen
    pygame.draw.rect(screen, (220, 60, 60), player_rect)  # Crimson red box

    # Refresh the display
    pygame.display.flip()

    # Maintain exactly 60 FPS
    clock.tick(FPS)

pygame.quit()
sys.exit()
