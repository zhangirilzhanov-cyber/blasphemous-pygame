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
# Create a rectangle at X=300, Y=200, with a Width=32 and Height=64 (knight proportions). Remember that it's from left upper angle coords
player_rect = pygame.Rect(300, 100, 32, 64)
player_speed = 4  # How many pixels the player moves per frame

# --- PHYSICS ---
player_y_velocity = 0  # Starts at 0 (not falling or jumping yet)
GRAVITY = 0.5  # The downward acceleration added to velocity every single frame
JUMP_FORCE = -10  # Negative because moving UP means decreasing Y coordinate
is_grounded = False  # A tracking flag to ensure we can't jump mid-air

# --- ENVIRONMENT PROPERTIES ---
# Create a rectangle at X=0, Y=320, stretching across the whole screen (Width=640), and 40 pixels thick
floor_rect = pygame.Rect(0, 320, 640, 40)

# --- THE GAME LOOP ---
running = True
while running:
    # --- PHASE 1: GET INPUT ---
    space_released_this_frame = False  # track if space/w was lifted rn
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Detect when a keyboard key is released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE or event.key == pygame.K_w:
                space_released_this_frame = True

    # Get a dictionary of all keyboard keys currently being held down
    keys = pygame.key.get_pressed()

    # --- PHASE 2: UPDATE LOGIC ---
    # Move left
    if keys[pygame.K_a]:
        player_rect.x -= player_speed
    # Move right
    if keys[pygame.K_d]:
        player_rect.x += player_speed

    # Screen boundaries (Keep the player inside the window)
    if player_rect.left < 0:
        player_rect.left = 0
    if player_rect.right > SCREEN_WIDTH:
        player_rect.right = SCREEN_WIDTH

    # --- PHASE 2: UPDATE LOGIC ---
    # (Keep your existing horizontal movement logic here...)

    # Apply Gravity
    player_y_velocity += GRAVITY  # Gravity accelerates your velocity down
    player_rect.y += player_y_velocity  # Move the player's Y position by that velocity

    # 2. Variable Jump Height Limit Check
    # If the player is moving UP (velocity < 0) AND they let go of the jump key...
    if player_y_velocity < 0 and space_released_this_frame:
        # Cut their upward speed in half! (e.g., changes -8 to -4)
        # This acts as your limit cap, giving an instant low jump.
        player_y_velocity *= 0.5
    is_grounded = False

    # Collision Detection with the Floor
    # .colliderect checks if the player box is physically overlapping the floor box
    if player_rect.colliderect(floor_rect):
        # If we hit the floor, snap the player's bottom right to the top of the floor
        player_rect.bottom = floor_rect.top
        player_y_velocity = 0  # Kill the downward velocity so we stop falling
        is_grounded = True

    if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and is_grounded:
        player_y_velocity = JUMP_FORCE  # Launch upwards!
        is_grounded = False

    # --- PHASE 3: RENDER (DRAW) ---
    screen.fill((40, 30, 45))  # Clear screen with dark purple

    # Draw our player rectangle onto the screen
    pygame.draw.rect(screen, (220, 60, 60), player_rect)  # Crimson red box

    # Draw our floor onto the screen
    pygame.draw.rect(screen, (75, 60, 80), floor_rect)  # Ash gray stone floor

    # Refresh the display
    pygame.display.flip()

    # Maintain exactly 60 FPS
    clock.tick(FPS)

pygame.quit()
sys.exit()
