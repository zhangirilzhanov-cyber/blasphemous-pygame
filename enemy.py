import pygame

class Enemy:
    def __init__(self, x, y, width=32, height=40, hp=3, enemy_id=None):
        self.enemy_id = enemy_id 
        # Physics & Hitbox
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (220, 60, 60)
        
        # Position Tracking
        self.pos_x = float(x)
        self.pos_y = float(y)
        
        # Physics Parameters
        self.speed = 1.5
        self.y_velocity = 0.0
        self.gravity = 0.5
        self.is_grounded = False
        
        # Patrol Mechanics
        self.direction = 1  
        self.patrol_timer = 0
        self.PATROL_SWITCH_TIME = 120  
        
        # Vision & Aggro Parameters
        self.detection_radius = 180
        self.is_chasing = False

        # Attack Parameters
        self.attack_range = 75       
        self.is_attacking = False
        self.attack_state = "idle"   
        self.attack_timer = 0
        
        self.WINDUP_FRAMES = 30     
        self.LUNGE_FRAMES = 12      
        self.COOLDOWN_FRAMES = 45   
        self.lunge_speed = 7.0      

        # Health & Invulnerability
        self.hp = hp
        self.max_hp = hp
        self.invulnerable = False
        self.i_frame_timer = 0
        self.I_FRAME_DURATION = 15 

        # Stun & Knockback Parameters
        self.is_stunned = False
        self.stun_timer = 0
        self.x_velocity = 0.0

    def apply_knockback(self, force_x, force_y, stun_duration=12):
        """Applies immediate knockback velocity and triggers stun lockout."""
        self.x_velocity = force_x
        self.y_velocity = force_y
        self.is_stunned = True
        self.stun_timer = stun_duration
        self.is_attacking = False
        self.attack_state = "idle"

    def take_damage(self, amount=1):
        if self.invulnerable:
            return False
            
        self.hp -= amount
        self.invulnerable = True
        self.i_frame_timer = self.I_FRAME_DURATION
        return self.hp <= 0  

    def clamp_to_screen(self, screen_width):
        """Prevents enemy from leaving the screen boundaries."""
        if self.rect.left < 0:
            self.rect.left = 0
            self.pos_x = float(self.rect.x)
            # Reverse patrol direction if hitting left boundary
            if not self.is_chasing:
                self.direction = 1

        elif self.rect.right > screen_width:
            self.rect.right = screen_width
            self.pos_x = float(self.rect.x)
            # Reverse patrol direction if hitting right boundary
            if not self.is_chasing:
                self.direction = -1

    def update(self, player, level, screen_width):
        # IMMUNITY and STUN TIMERS 
        if self.invulnerable:
            self.i_frame_timer -= 1
            if self.i_frame_timer <= 0:
                self.invulnerable = False

        # Handle Stun Recovery
        if self.is_stunned:
            self.stun_timer -= 1
            if self.stun_timer <= 0:
                self.is_stunned = False
                self.x_velocity = 0.0
            else:
                # Apply knockback momentum friction
                self.pos_x += self.x_velocity
                self.x_velocity *= 0.85
                self.rect.x = round(self.pos_x)

                # Still apply gravity during stun
                self.y_velocity += self.gravity
                self.pos_y += self.y_velocity
                self.rect.y = round(self.pos_y)

                collided_floor = level.check_floor_collisions(self.rect)
                if collided_floor:
                    self.rect.bottom = collided_floor.top
                    self.pos_y = float(self.rect.y)
                    self.y_velocity = 0.0
                return  # Skip AI/attack logic while stunned

        # --- 1. NORMAL AI and ATTACK LOGIC ---
        distance_to_player = pygame.math.Vector2(self.rect.center).distance_to(player.rect.center)
        self.is_chasing = distance_to_player <= self.detection_radius

        if self.is_attacking:
            self.attack_timer -= 1
            if self.attack_state == "windup":
                if self.attack_timer <= 0:
                    self.attack_state = "lunge"
                    self.attack_timer = self.LUNGE_FRAMES
            elif self.attack_state == "lunge":
                self.pos_x += self.direction * self.lunge_speed
                if self.attack_timer <= 0:
                    self.attack_state = "cooldown"
                    self.attack_timer = self.COOLDOWN_FRAMES
            elif self.attack_state == "cooldown" and self.attack_timer <= 0:
                self.is_attacking = False
                self.attack_state = "idle"
        else:
            if distance_to_player <= self.attack_range:
                self.is_attacking = True
                self.attack_state = "windup"
                self.attack_timer = self.WINDUP_FRAMES
                dx = player.rect.centerx - self.rect.centerx
                self.direction = 1 if dx > 0 else -1
            elif self.is_chasing:
                dx = player.rect.centerx - self.rect.centerx
                if abs(dx) > 2:     #otherwise it would jitter in the player 
                    move_dir = 1 if dx > 0 else -1
                    self.pos_x += move_dir * self.speed
                    self.direction = move_dir
            else:
                self.pos_x += self.direction * self.speed
                self.patrol_timer += 1
                if self.patrol_timer >= self.PATROL_SWITCH_TIME:
                    self.direction *= -1
                    self.patrol_timer = 0
        

        self.rect.x = round(self.pos_x)

        # pysics and gravity
        self.y_velocity += self.gravity
        self.pos_y += self.y_velocity
        self.rect.y = round(self.pos_y)

        self.is_grounded = False
        collided_floor = level.check_floor_collisions(self.rect)
        if collided_floor:
            self.rect.bottom = collided_floor.top
            self.pos_y = float(self.rect.y)
            self.y_velocity = 0.0
            self.is_grounded = True
        
        self.clamp_to_screen(screen_width)

    def draw(self, screen):
        if self.invulnerable and (self.i_frame_timer // 3) % 2 == 0: # Blinking math for ticks
            pygame.draw.rect(screen, (255, 255, 255), self.rect)
            return

        body_color = self.color
        if self.is_stunned:
            body_color = (180, 100, 100)  # Pale/dull red when stunned
        elif self.attack_state == "windup":
            body_color = (255, 180, 0) if (self.attack_timer // 4) % 2 == 0 else (255, 80, 0)
        elif self.attack_state == "lunge":
            body_color = (255, 20, 20)
        elif self.attack_state == "cooldown":
            body_color = (130, 40, 40)

        pygame.draw.rect(screen, body_color, self.rect)

        if (self.is_chasing or self.is_attacking) and not self.is_stunned:
            eye_color = (255, 255, 255) if not self.is_attacking else (255, 255, 0)
            pygame.draw.rect(screen, eye_color, (self.rect.x + 4, self.rect.y + 6, 8, 8))
            pygame.draw.rect(screen, eye_color, (self.rect.right - 12, self.rect.y + 6, 8, 8))

class Boss(Enemy):
    def __init__(self, x, y):
        # Larger hit box (64x80) and higher HP (12 HP)
        super().__init__(x, y, width=64, height=80, hp=12)
        
        self.color = (140, 20, 60)
        self.speed = 2.0
        self.lunge_speed = 10.0      # Faster lunge
        self.attack_range = 140      # Broader attack range
        
        # Faster recovery and windup
        self.WINDUP_FRAMES = 24
        self.LUNGE_FRAMES = 15
        self.COOLDOWN_FRAMES = 30

    def draw(self, screen):
        # White damage flash
        if self.invulnerable and (self.i_frame_timer // 3) % 2 == 0:
            pygame.draw.rect(screen, (255, 255, 255), self.rect)
            return

        body_color = self.color
        if self.is_stunned:
            body_color = (120, 50, 80)
        elif self.attack_state == "windup":
            body_color = (255, 50, 0) if (self.attack_timer // 3) % 2 == 0 else (255, 140, 0)
        elif self.attack_state == "lunge":
            body_color = (255, 0, 80)

        pygame.draw.rect(screen, body_color, self.rect)

        # Draw Boss Health Bar above head
        bar_w, bar_h = 60, 6
        bar_x = self.rect.centerx - (bar_w // 2)
        bar_y = self.rect.y - 14
        
        health_pct = max(0, self.hp / self.max_hp)
        pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(screen, (220, 40, 40), (bar_x, bar_y, int(bar_w * health_pct), bar_h))
        pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_w, bar_h), width=1)