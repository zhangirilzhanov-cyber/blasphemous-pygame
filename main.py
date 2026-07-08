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

# --- DASH MECHANIC ---
player_facing_right = True  # Track direction so we dash the right way
is_dashing = False          # Are we currently in a dash state?
dash_timer = 0              # How long the dash lasts (in frames)
DASH_DURATION = 10          # Dash lasts for 10 frames (~0.16 seconds)
DASH_SPEED = 12             # Triple our normal speed!
dash_cooldown = 0           # Current cooldown timer (0 means ready to dash)
DASH_COOLDOWN_TIME = 45     #  Cooldown lasts 45 frames (~0.75 seconds)

floor_rect = pygame.Rect(0, 320, 640, 40)

# --- 3. MODULAR LOGIC BLOCKS (FUNCTIONS) ---

def handle_input():
    """Handles keyboard presses and returns input flags."""
    global player_y_velocity, is_grounded, player_facing_right, is_dashing, dash_timer
    
    keys = pygame.key.get_pressed()
    space_released_this_frame = False
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE or event.key == pygame.K_w:
                space_released_this_frame = True

    # If currently dashing, freeze regular keyboard inputs!
    if is_dashing:
        return space_released_this_frame

    # Horizontal Movement & Tracking Direction
    if keys[pygame.K_a]:
        player_rect.x -= player_speed
        player_facing_right = False  # Facing Left
    if keys[pygame.K_d]:
        player_rect.x += player_speed
        player_facing_right = True   # Facing Right

    # Trigger Dash (Left Shift)
    if keys[pygame.K_LSHIFT] and dash_cooldown == 0:
        is_dashing = True
        dash_timer = DASH_DURATION
        # Give an instant burst of speed in the direction we are facing
        player_y_velocity = 0  # Clear any falling momentum when dash starts

    # Initial Jump Trigger
    if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and is_grounded:
        player_y_velocity = JUMP_FORCE
        is_grounded = False

    return space_released_this_frame


def update_physics(space_released_this_frame):
    """Calculates gravity, variable jump capping, and collisions."""
    global player_y_velocity, is_grounded, is_dashing, dash_timer, dash_cooldown

    # 🌟 Handle Dash Physics State
    if is_dashing:
        # Move character at high speed based on direction
        if player_facing_right:
            player_rect.x += DASH_SPEED
        else:
            player_rect.x -= DASH_SPEED
            
        dash_timer -= 1  # Countdown the frames
        if dash_timer <= 0:
            is_dashing = False  # Dash finished, return to regular state
            dash_cooldown = DASH_COOLDOWN_TIME # 🌟 Start the cooldown penalty now!
            
        # Keep character bound to the screen limits during dash
        if player_rect.left < 0: 
            player_rect.left = 0
        if player_rect.right > SCREEN_WIDTH:    
            player_rect.right = SCREEN_WIDTH
        return  # Bypass gravity and floor calculations while dashing!

    #Regular Physics State (runs only if NOT dashing)
    
    # Countdown our recovery cooldown frame by frame until it hits 0
    if dash_cooldown > 0:
        dash_cooldown -= 1
    
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
