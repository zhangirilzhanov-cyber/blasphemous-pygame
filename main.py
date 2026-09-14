import sys
import pygame
from level import Level
from player import Player, InputState

# --- 1. ENGINE SETUP ---
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 360
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("My Blasphemous Project")

clock = pygame.time.Clock()
FPS = 60

# --- 2. GAME OBJECTS & FONTS ---
font = pygame.font.SysFont("arial", 32, bold=True)
small_font = pygame.font.SysFont("arial", 16)

defeated_enemies: set[str] = set()
current_level = Level("room_1", defeated_enemies)
current_level.load_room("room_1", defeated_enemies)

player = Player(300, 100)

a_press_time = 0
d_press_time = 0


def gather_inputs(events):
    """Builds a frame-accurate snapshot of all keys and mouse inputs."""
    global a_press_time, d_press_time

    inputs = InputState()
    keys = pygame.key.get_pressed()
    current_time = pygame.time.get_ticks()

    inputs.up_held = keys[pygame.K_w]

    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                current_level.interact_with_items(player)
            if event.key == pygame.K_a:
                a_press_time = current_time
            if event.key == pygame.K_d:
                d_press_time = current_time

            if event.key == pygame.K_SPACE:
                inputs.jump_requested = True
            if event.key == pygame.K_LSHIFT:
                inputs.dash_pressed = True
            if event.key == pygame.K_RETURN:
                inputs.attack_pressed = True
            if event.key == pygame.K_u:
                inputs.toggle_dash = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                inputs.space_released = True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            inputs.attack_pressed = True

    # Horizontal Movement Priority
    a_held = keys[pygame.K_a]
    d_held = keys[pygame.K_d]

    if a_held and d_held:
        if a_press_time > d_press_time:
            inputs.move_left = True
        else:
            inputs.move_right = True
    elif a_held:
        inputs.move_left = True
    elif d_held:
        inputs.move_right = True

    return inputs


def draw_health_ui(surface, current_hp, max_hp):
    """Draws heart indicators in the top-left corner of the screen."""
    start_x = 16
    start_y = 16
    spacing = 20

    for i in range(max_hp):
        x = start_x + (i * spacing)
        y = start_y

        if i < current_hp:
            # Filled Red Heart
            pygame.draw.rect(surface, (220, 50, 50), (x, y, 6, 6))
            pygame.draw.rect(surface, (220, 50, 50), (x + 6, y, 6, 6))
            pygame.draw.polygon(
                surface, (220, 50, 50), [(x, y + 4), (x + 12, y + 4), (x + 6, y + 12)]
            )
        else:
            # Empty Heart Outline
            pygame.draw.polygon(
                surface,
                (80, 60, 70),
                [(x, y), (x + 12, y), (x + 12, y + 6), (x + 6, y + 12), (x, y + 6)],
                width=2,
            )


def draw_game_over_ui(surface):
    """Renders semi-transparent overlay and death prompt."""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((20, 10, 15))
    surface.blit(overlay, (0, 0))

    text = font.render("YOU DIED", True, (220, 40, 40))
    prompt = small_font.render("Press SPACE or ENTER to Respawn", True, (200, 200, 200))

    surface.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 130))
    surface.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, 180))


def check_pitfalls_and_transitions(player, level, screen_width, screen_height, defeated_enemies):
    """Handles 4-way transitions with explicit safe spawn points."""
    
    # Block transitions while boss is locked
    if getattr(level, "is_locked", False):
        if player.rect.left < 0:
            player.rect.left = 0
            player.pos_x = float(player.rect.x)
        elif player.rect.right > screen_width:
            player.rect.right = screen_width
            player.pos_x = float(player.rect.x)
        if player.rect.top < 0:
            player.rect.top = 0
            player.pos_y = float(player.rect.y)
        return

    # --- UPWARD TRANSITION (Climbing out of room_4 into room_3) ---
    if player.rect.bottom < 0:
        next_room = level.exits.get("up")
        if next_room:
            level.load_room(next_room, defeated_enemies)
            
            # Check for hardcoded spawn point in JSON
            spawn = getattr(level, "spawns", {}).get("from_down")
            if spawn:
                player.pos_x = float(spawn["x"])
                player.pos_y = float(spawn["y"])
                player.rect.x = round(player.pos_x)
                player.rect.y = round(player.pos_y)
            else:
                player.rect.bottom = screen_height - 10
                player.pos_y = float(player.rect.y)
            
            player.y_velocity = 0.0
            player.last_grounded_pos = (player.rect.x, player.rect.y)
        else:
            player.rect.top = 0
            player.pos_y = float(player.rect.y)
        return

    # --- DOWNWARD TRANSITION ---
    if player.rect.top > screen_height:
        next_room = level.exits.get("down")
        if next_room:
            level.load_room(next_room, defeated_enemies)
            
            spawn = getattr(level, "spawns", {}).get("from_up")
            if spawn:
                player.pos_x = float(spawn["x"])
                player.pos_y = float(spawn["y"])
                player.rect.x = round(player.pos_x)
                player.rect.y = round(player.pos_y)
            else:
                player.rect.top = 0
                player.pos_y = float(player.rect.y)
                
            player.last_grounded_pos = (player.rect.x, player.rect.y)
        else:
            player.take_damage(1)
            player.respawn()
        return

    # --- HORIZONTAL TRANSITIONS ---
    if player.rect.left > screen_width:
        next_room = level.exits.get("right")
        if next_room:
            level.load_room(next_room, defeated_enemies)
            
            spawn = getattr(level, "spawns", {}).get("from_left")
            if spawn:
                player.pos_x = float(spawn["x"])
                player.pos_y = float(spawn["y"])
                player.rect.x = round(player.pos_x)
                player.rect.y = round(player.pos_y)
            else:
                player.rect.left = 0
                player.pos_x = float(player.rect.x)
                
            player.last_grounded_pos = (player.rect.x, player.rect.y)

    elif player.rect.right < 0:
        next_room = level.exits.get("left")
        if next_room:
            level.load_room(next_room, defeated_enemies)
            
            spawn = getattr(level, "spawns", {}).get("from_right")
            if spawn:
                player.pos_x = float(spawn["x"])
                player.pos_y = float(spawn["y"])
                player.rect.x = round(player.pos_x)
                player.rect.y = round(player.pos_y)
            else:
                player.rect.right = screen_width
                player.pos_x = float(player.rect.x)
                
            player.last_grounded_pos = (player.rect.x, player.rect.y)


# --- 3. MAIN GAME LOOP ---
running = True
game_over = False

while running:
    events = pygame.event.get()

    if game_over:
        # Check for restart press
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and (
                event.key == pygame.K_SPACE or event.key == pygame.K_RETURN
            ):
                # Reset game state & player back to room 1
                current_level.load_room("room_1", defeated_enemies)
                player.hp = player.max_hp
                player.invulnerable = False
                player.rect.topleft = (300, 100)
                player.last_grounded_pos = (300, 100)
                player.y_velocity = 0
                game_over = False
    else:
        # Normal Gameplay Loop
        inputs = gather_inputs(events)

        space_released = player.handle_input(inputs)
        player.update(space_released, current_level)

        # Phase 2 & 3: Game State & Enemy AI Updates

        current_level.update(player, SCREEN_WIDTH)  # Run enemy vision, patrol, & physics
        current_level.update_combat(player, defeated_enemies)

        check_pitfalls_and_transitions(
            player, current_level, SCREEN_WIDTH, SCREEN_HEIGHT, defeated_enemies
        )

        # Trigger Game Over condition
        if player.hp <= 0:
            game_over = True

    # Render Phase
    screen.fill((40, 30, 45))
    current_level.draw(screen)
    player.draw(screen)
    draw_health_ui(screen, player.hp, player.max_hp)

    if game_over:
        draw_game_over_ui(screen)
        defeated_enemies.clear()

    pygame.display.flip()
    clock.tick(FPS)
