import pygame


class InputState:
    """Stores the frame-accurate state of all inputs."""

    def __init__(self):
        self.move_left = False
        self.move_right = False
        self.up_held = False
        self.jump_requested = False
        self.space_released = False
        self.dash_pressed = False
        self.attack_pressed = False
        self.toggle_dash = False


class Player:
    def __init__(self, x, y):
        # Physics Box & Visuals
        self.rect = pygame.Rect(x, y, 32, 64)
        self.color = (60, 160, 220)  # Blue Knight Body

        self.jump_buffer = 0
        self.JUMP_BUFFER_TIME = 8

        # Physics Parameters
        self.speed = 4
        self.y_velocity = 0
        self.gravity = 0.5
        self.jump_force = -11
        self.is_grounded = False
        self.facing_right = True

        # Fall Tracking & Respawn Positions
        self.last_grounded_pos = (x, y)
        self.fall_start_y = y
        self.FALL_DAMAGE_THRESHOLD = 160  # Falling >160px deals damage

        # Dash Ability
        self.has_dash = False
        self.is_dashing = False
        self.dash_timer = 0
        self.dash_duration = 10
        self.dash_speed = 12
        self.dash_cooldown = 0
        self.dash_cooldown_time = 45

        # Combat Parameters
        self.is_attacking = False
        self.attack_timer = 0
        self.attack_duration = 12
        self.attack_rect = None
        self.attack_type = "neutral"

        # Health & Immunity
        self.hp = 20
        self.max_hp = 20
        self.invulnerable = False
        self.i_frame_timer = 0
        self.I_FRAME_DURATION = 60

        #stun
        self.is_stunned = False
        self.stun_timer = 0
        self.x_velocity = 0.0

    def respawn(self):
        """Teleports player back to the last safe grounded position."""
        self.rect.topleft = self.last_grounded_pos
        self.y_velocity = 0

    @property
    def hurtbox(self):
        return self.rect

    def take_damage(self, amount=1):
        if self.invulnerable or self.is_dashing:
            return False
        self.hp -= amount
        self.invulnerable = True
        self.i_frame_timer = self.I_FRAME_DURATION
    
    def apply_knockback(self, force_x, force_y, stun_duration=10):
        """Applies hit impact force and locks controls briefly."""
        self.x_velocity = force_x
        self.y_velocity = force_y
        self.is_stunned = True
        self.stun_timer = stun_duration
        self.is_attacking = False
        self.is_dashing = False

    def handle_input(self, inputs: InputState):
        """Processes a frame-accurate snapshot of user inputs."""
        if self.is_stunned:
            return inputs.space_released
        
        if inputs.toggle_dash:
            self.has_dash = not self.has_dash

        # Combat Trigger
        if inputs.attack_pressed and not self.is_attacking:
            self.is_attacking = True
            self.attack_timer = self.attack_duration

            if inputs.up_held:
                self.attack_type = "upslash"
            else:
                self.attack_type = "neutral"

        if self.is_dashing:
            return inputs.space_released

        # Horizontal Movement
        if inputs.move_left:
            self.rect.x -= self.speed
            self.facing_right = False
        if inputs.move_right:
            self.rect.x += self.speed
            self.facing_right = True

        # Dash Trigger
        if inputs.dash_pressed and self.has_dash and self.dash_cooldown == 0:
            self.is_dashing = True
            self.dash_timer = self.dash_duration
            self.y_velocity = 0

        # Jump Buffer Logic
        if inputs.jump_requested:
            self.jump_buffer = self.JUMP_BUFFER_TIME
        elif self.jump_buffer > 0:
            self.jump_buffer -= 1

        if self.jump_buffer > 0 and self.is_grounded:
            self.y_velocity = self.jump_force
            self.is_grounded = False
            self.jump_buffer = 0

        return inputs.space_released

    def update(self, space_released, level):
        # Immunity Timers
        if self.invulnerable:
            self.i_frame_timer -= 1
            if self.i_frame_timer <= 0:
                self.invulnerable = False

        if self.is_stunned:
            self.stun_timer -= 1
            self.rect.x += int(self.x_velocity)
            self.x_velocity *= 0.85
            if self.stun_timer <= 0:
                self.is_stunned = False
                self.x_velocity = 0.0

        # Weapon Extension Geometry
        if self.is_attacking:
            self.attack_timer -= 1
            if self.attack_type == "upslash":
                self.attack_rect = pygame.Rect(
                    self.rect.x + 4, self.rect.y - 32, 24, 32
                )
            else:
                if self.facing_right:
                    self.attack_rect = pygame.Rect(
                        self.rect.right, self.rect.y + 20, 32, 16
                    )
                else:
                    self.attack_rect = pygame.Rect(
                        self.rect.left - 32, self.rect.y + 20, 32, 16
                    )

            if self.attack_timer <= 0:
                self.is_attacking = False
                self.attack_rect = None
        else:
            self.attack_rect = None

        # Dash Movement
        if self.is_dashing:
            if self.facing_right:
                self.rect.x += self.dash_speed
            else:
                self.rect.x -= self.dash_speed

            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.is_dashing = False
                self.dash_cooldown = self.dash_cooldown_time
            return

        # Regular Physics
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1

        self.y_velocity += self.gravity
        self.rect.y += self.y_velocity

        if self.y_velocity < 0 and space_released:
            self.y_velocity *= 0.5

        # Floor Collisions & Fall Damage Calculation
        was_grounded = self.is_grounded
        self.is_grounded = False
        collided_floor = level.check_floor_collisions(self.rect)

        if collided_floor:
            self.rect.bottom = collided_floor.top

            # If landing from airborne state, check fall distance
            if not was_grounded:
                fall_distance = self.rect.y - self.fall_start_y
                if fall_distance > self.FALL_DAMAGE_THRESHOLD:
                    self.take_damage(1)
                    self.respawn()
                    return  # Instantly teleport back

            # Update safe anchor position while standing on ground
            self.y_velocity = 0
            self.is_grounded = True
            self.last_grounded_pos = self.rect.topleft
            self.fall_start_y = self.rect.y
        else:
            # Mark starting Y when stepping off a ledge or starting a jump
            if was_grounded:
                self.fall_start_y = self.rect.y

    def draw(self, screen):
        # Flashing i-frame animation
        if self.invulnerable and (self.i_frame_timer // 6) % 2 == 0:
            pass
        else:
            pygame.draw.rect(screen, self.color, self.rect)

        # Render Active Blade Rectangle
        if self.attack_rect:
            pygame.draw.rect(screen, (240, 240, 255), self.attack_rect)
