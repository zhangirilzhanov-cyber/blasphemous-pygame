import json

import pygame

from enemy import Boss, Enemy
from item import Item
from sign import Sign


class Level:
    def __init__(self, room_id, defeated_enemies):
        self.current_room_id = room_id
        self.floors = []
        self.enemies = []
        self.signs = []
        self.items = []
        self.exits = {}
        self.load_room(room_id, defeated_enemies)

    def load_room(self, room_id, defeated_enemies):
        self.current_room_id = room_id
        with open("levels.json", "r") as f:
            data = json.load(f)
        
        room_data = data.get(room_id, {})
        self.exits = room_data.get("exits", {})
        self.spawns = room_data.get("spawns", {})

        self.floors = [
            pygame.Rect(f["x"], f["y"], f["w"], f["h"]) 
            for f in room_data.get("floors", [])
        ]
        
        self.enemies = []
        for e in room_data.get("enemies", []):
            enemy_id = e.get("id")
            if enemy_id and enemy_id in defeated_enemies:
                continue  # Skip spawning this enemy

            if e.get("type") == "boss":
                boss = Boss(e["x"], e["y"])
                boss.enemy_id = enemy_id
                self.enemies.append(boss)
            else:
                self.enemies.append(
                    Enemy(e["x"], e["y"], e.get("w", 32), e.get("h", 40), hp=e.get("hp", 3), enemy_id=enemy_id)
                )

        self.signs = [
            Sign(s["x"], s["y"], s["text"])
            for s in room_data.get("signs", [])
        ]

        # Load Items
        self.items = [
            Item(i["x"], i["y"], i.get("type", "dash"))
            for i in room_data.get("items", [])
        ]

    def check_floor_collisions(self, rect):
        for floor in self.floors:
            if rect.colliderect(floor):
                return floor
        return None

    def update(self, player, screen_width=640):
        # Track whether boss is active
        was_locked = getattr(self, "is_locked", False)
        self.is_locked = any(isinstance(e, Boss) for e in self.enemies)

        # Trigger platform spawn when the boss is defeated
        if was_locked and not self.is_locked:
            self.spawn_exit_platforms()

        for enemy in self.enemies:
            enemy.update(player, self, screen_width)
            
        for sign in self.signs:
            sign.check_interaction(player.rect)

        for item in self.items:
            item.update()
            item.check_interaction(player.rect)

    def spawn_exit_platforms(self):
        """Spawns stepping platforms to climb back up to room_3."""
        # Check if platforms already exist to avoid duplicates
        if len(self.floors) == 1:
            self.floors.extend([
                pygame.Rect(200, 240, 100, 20),
                pygame.Rect(340, 160, 100, 20),
                pygame.Rect(200, 80, 120, 20)
            ])

    def interact_with_items(self, player):
        """Triggers when W key is pressed near an item."""
        for item in self.items[:]:
            if item.is_player_near:
                if item.item_type == "dash":
                    player.has_dash = True  # Unlock dash upgrade
                self.items.remove(item)

    def update_combat(self, player, defeated_enemies):
        if player.attack_rect:
            for enemy in self.enemies[:]:
                if player.attack_rect.colliderect(enemy.rect):  
                    if not enemy.invulnerable:
                        direction = 1 if enemy.rect.centerx > player.rect.centerx else -1
                        if player.attack_type == "upslash":
                            enemy.apply_knockback(direction * 2, -7, stun_duration=15)
                        else:
                            enemy.apply_knockback(direction * 8, -3, stun_duration=12)

                        is_dead = enemy.take_damage(1)
                        if is_dead:
                            # Add unique ID to persistent set upon death
                            if enemy.enemy_id: # Can add more incapsulation in the future
                                defeated_enemies.add(enemy.enemy_id)
                            self.enemies.remove(enemy)

        for enemy in self.enemies:
            if player.hurtbox.colliderect(enemy.rect):
                if not player.invulnerable and not player.is_dashing:
                    direction = 1 if player.rect.centerx > enemy.rect.centerx else -1
                    player.apply_knockback(direction * 7, -4, stun_duration=12)
                    player.take_damage(1)

    def draw(self, screen):
        for floor in self.floors:
            pygame.draw.rect(screen, (75, 60, 80), floor)

        if getattr(self, "is_locked", False):
            # Vertical lock bars on screen edges
            pygame.draw.rect(screen, (180, 40, 40), (0, 0, 12, 360))
            pygame.draw.rect(screen, (180, 40, 40), (628, 0, 12, 360))
        
        for enemy in self.enemies:
            enemy.draw(screen)
        for sign in self.signs:
            sign.draw(screen)
        for item in self.items:
            item.draw(screen)