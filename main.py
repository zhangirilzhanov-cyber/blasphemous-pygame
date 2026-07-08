import pygame
import sys

# --- 1. ENGINE SETUP ---
pygame.init()
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 360
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("My Blasphemous Project")

clock = pygame.time.Clock()
FPS = 60

# --- 2. GAME STATE (VARIABLES) ---
player_rect = pygame.Rect(300, 100, 32, 64)
player_speed = 4  

player_y_velocity = 0  
GRAVITY = 0.5           
JUMP_FORCE = -11       
is_grounded = False    

floor_rect = pygame.Rect(0, 320, 640, 40)

# --- 3. MODULAR LOGIC BLOCKS (FUNCTIONS) ---

def handle_input():
    """Handles keyboard presses and returns input flags."""
    global player_y_velocity, is_grounded
    
    keys = pygame.key.get_pressed()
    space_released_this_frame = False
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE or event.key == pygame.K_w:
                space_released_this_frame = True

    # Horizontal Movement
    if keys[pygame.K_a]:
        player_rect.x -= player_speed
    if keys[pygame.K_d]:
        player_rect.x += player_speed

    # Initial Jump Trigger
    if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and is_grounded:
        player_y_velocity = JUMP_FORCE
        is_grounded = False

    return space_released_this_frame


def update_physics(space_released_this_frame):
    """Calculates gravity, variable jump capping, and collisions."""
    global player_y_velocity, is_grounded

    # Apply Gravity
    player_y_velocity += GRAVITY
    player_rect.y += player_y_velocity

    # Variable Jump Height Limit Check
    if player_y_velocity < 0 and space_released_this_frame:
        player_y_velocity *= 0.5 

    # Floor Collision Logic
    is_grounded = False
    if player_rect.colliderect(floor_rect):
        player_rect.bottom = floor_rect.top
        player_y_velocity = 0
        is_grounded = True


def render_screen():
    """Wipes the display buffer and draws all objects from zero."""
    screen.fill((40, 30, 45))                      # Dark Purple Background
    pygame.draw.rect(screen, (75, 60, 80), floor_rect)    # Ash Gray Floor
    pygame.draw.rect(screen, (220, 60, 60), player_rect)  # Crimson Knight Box
    pygame.display.flip()                          # Double Buffer Flip


# --- 4. THE MAIN GAME LOOP ---
running = True
while running:
    # Phase 1: Get Input
    space_released = handle_input()
    
    # Phase 2: Update positions/physics
    update_physics(space_released)
    
    # Phase 3: Draw everything
    render_screen()
    
    # Maintain frame rate
    clock.tick(FPS)
