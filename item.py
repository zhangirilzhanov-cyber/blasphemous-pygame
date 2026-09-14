import pygame
import math

class Item:
    def __init__(self, x, y, item_type="dash"):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.base_y = float(y)
        self.item_type = item_type
        
        # Floating & Shining Animation parameters
        self.anim_timer = 0
        self.is_player_near = False
        self.font = pygame.font.SysFont("arial", 14)

    def check_interaction(self, player_rect):
        """Checks if the player is standing near the item."""
        interact_box = self.rect.inflate(40, 30)
        self.is_player_near = interact_box.colliderect(player_rect)

    def update(self):
        """Hover floating animation."""
        self.anim_timer += 0.08
        # Gentle floating oscillation up and down
        self.rect.y = round(self.base_y + math.sin(self.anim_timer) * 5)

    def draw(self, screen):
        # 1. Pulsing Outer Glow Aura
        glow_size = int(14 + math.sin(self.anim_timer * 2) * 4)
        glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (255, 220, 100, 120), (glow_size, glow_size), glow_size)
        screen.blit(glow_surface, glow_surface.get_rect(center=self.rect.center))

        # 2. Shiny Core Gem
        pygame.draw.rect(screen, (255, 255, 200), self.rect)
        pygame.draw.rect(screen, (255, 180, 0), self.rect, width=2)

        # 3. Prompt ("Press W")
        if self.is_player_near:
            text_surface = self.font.render("[W] Pick Up", True, (255, 255, 255))
            padding = 4
            bg_rect = pygame.Rect(
                self.rect.centerx - (text_surface.get_width() // 2) - padding,
                self.rect.y - 28,
                text_surface.get_width() + (padding * 2),
                text_surface.get_height() + 2
            )
            pygame.draw.rect(screen, (20, 15, 25), bg_rect)
            pygame.draw.rect(screen, (255, 200, 50), bg_rect, width=1)
            screen.blit(text_surface, (bg_rect.x + padding, bg_rect.y + 1))