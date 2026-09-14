import pygame

class Sign:
    def __init__(self, x, y, text):
        self.rect = pygame.Rect(x, y, 24, 32)
        self.text = text
        self.font = pygame.font.SysFont("arial", 14)
        self.is_player_near = False

    def check_interaction(self, player_rect):
        """Checks if the player is standing next to the sign."""
        # Expand detection box slightly around the sign
        interact_box = self.rect.inflate(30, 20)
        self.is_player_near = interact_box.colliderect(player_rect)

    def draw(self, screen):
        # Draw wooden sign post & board
        pygame.draw.rect(screen, (100, 60, 30), (self.rect.x + 9, self.rect.y + 12, 6, 20))  # Post
        pygame.draw.rect(screen, (160, 110, 60), (self.rect.x, self.rect.y, 24, 16))          # Board
        pygame.draw.rect(screen, (80, 50, 20), (self.rect.x, self.rect.y, 24, 16), width=1)   # Border

        # Render message bubble when player walks close
        if self.is_player_near:
            text_surface = self.font.render(self.text, True, (240, 240, 240))
            padding = 6
            bg_rect = pygame.Rect(
                self.rect.centerx - (text_surface.get_width() // 2) - padding,
                self.rect.y - 30,
                text_surface.get_width() + (padding * 2),
                text_surface.get_height() + 4
            )
            pygame.draw.rect(screen, (20, 15, 25), bg_rect)
            pygame.draw.rect(screen, (200, 170, 100), bg_rect, width=1)
            screen.blit(text_surface, (bg_rect.x + padding, bg_rect.y + 2))