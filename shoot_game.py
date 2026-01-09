import pygame
import random
import math
from enum import Enum

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Create the game screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Shooting Game")

# Clock for frame rate
clock = pygame.time.Clock()
FPS = 60

# Font for text
font_large = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 36)


class GameState(Enum):
    PLAYING = 1
    GAME_OVER = 2


class Player(pygame.sprite.Sprite):
    """Player character with movement and shooting capabilities"""
    
    def __init__(self, x, y):
        super().__init__()
        self.width = 40
        self.height = 50
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 5
        self.health = 100
        
    def update(self):
        """Update player position based on input"""
        keys = pygame.key.get_pressed()
        
        # Movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed
        
        # Boundary checking
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - self.width))
        self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - self.height))
    
    def draw_health(self, surface):
        """Draw health bar above player"""
        bar_width = 40
        bar_height = 5
        fill = (self.health / 100) * bar_width
        
        outline_rect = pygame.Rect(self.rect.x - 5, self.rect.y - 15, bar_width, bar_height)
        fill_rect = pygame.Rect(self.rect.x - 5, self.rect.y - 15, fill, bar_height)
        
        pygame.draw.rect(surface, RED, outline_rect)
        pygame.draw.rect(surface, GREEN, fill_rect)
        pygame.draw.rect(surface, WHITE, outline_rect, 1)


class Bullet(pygame.sprite.Sprite):
    """Bullet fired by player"""
    
    def __init__(self, x, y):
        super().__init__()
        self.width = 5
        self.height = 15
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -10
        
    def update(self):
        """Move bullet up"""
        self.rect.y += self.speed
        
        # Remove if off screen
        if self.rect.bottom < 0:
            self.kill()


class Enemy(pygame.sprite.Sprite):
    """Enemy that moves toward player and shoots"""
    
    def __init__(self, x, y):
        super().__init__()
        self.width = 35
        self.height = 35
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = random.uniform(1, 2)
        self.health = 20
        self.shoot_timer = random.randint(30, 90)
        
    def update(self):
        """Move downward and occasionally shoot"""
        self.rect.y += self.speed
        self.shoot_timer -= 1
        
        # Remove if off screen
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
    
    def shoot(self):
        """Determine if enemy should shoot"""
        if self.shoot_timer <= 0:
            self.shoot_timer = random.randint(30, 90)
            return True
        return False
    
    def draw_health(self, surface):
        """Draw health bar above enemy"""
        bar_width = 30
        bar_height = 3
        fill = (self.health / 20) * bar_width
        
        outline_rect = pygame.Rect(self.rect.x - 2, self.rect.y - 10, bar_width, bar_height)
        fill_rect = pygame.Rect(self.rect.x - 2, self.rect.y - 10, fill, bar_height)
        
        pygame.draw.rect(surface, RED, outline_rect)
        pygame.draw.rect(surface, YELLOW, fill_rect)
        pygame.draw.rect(surface, WHITE, outline_rect, 1)


class EnemyBullet(pygame.sprite.Sprite):
    """Bullet fired by enemy"""
    
    def __init__(self, x, y):
        super().__init__()
        self.width = 5
        self.height = 15
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speed = 7
        
    def update(self):
        """Move bullet down"""
        self.rect.y += self.speed
        
        # Remove if off screen
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Game:
    """Main game class"""
    
    def __init__(self):
        self.state = GameState.PLAYING
        self.score = 0
        self.wave = 1
        self.enemy_spawn_timer = 0
        self.enemies_spawned = 0
        self.enemies_killed = 0
        
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        
        # Create player
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60)
        self.all_sprites.add(self.player)
        
        # Game configuration
        self.max_enemies = 5 + (self.wave * 2)
        self.spawn_rate = max(30, 60 - (self.wave * 5))
        
    def spawn_enemy(self):
        """Spawn a new enemy"""
        if self.enemies_spawned < self.max_enemies and self.enemy_spawn_timer <= 0:
            x = random.randint(0, SCREEN_WIDTH - 35)
            y = random.randint(-100, -40)
            enemy = Enemy(x, y)
            self.all_sprites.add(enemy)
            self.enemies.add(enemy)
            self.enemies_spawned += 1
            self.enemy_spawn_timer = self.spawn_rate
        else:
            self.enemy_spawn_timer -= 1
    
    def next_wave(self):
        """Progress to next wave"""
        self.wave += 1
        self.enemies_spawned = 0
        self.enemies_killed = 0
        self.max_enemies = 5 + (self.wave * 2)
        self.spawn_rate = max(30, 60 - (self.wave * 5))
    
    def handle_input(self):
        """Handle player input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Shoot
                    bullet = Bullet(self.player.rect.centerx, self.player.rect.top)
                    self.all_sprites.add(bullet)
                    self.bullets.add(bullet)
                elif event.key == pygame.K_r and self.state == GameState.GAME_OVER:
                    # Restart game
                    self.__init__()
        return True
    
    def update(self):
        """Update game state"""
        if self.state == GameState.GAME_OVER:
            return
        
        self.all_sprites.update()
        self.spawn_enemy()
        
        # Check if all enemies defeated
        if self.enemies_spawned >= self.max_enemies and len(self.enemies) == 0:
            self.next_wave()
        
        # Enemy shooting
        for enemy in self.enemies:
            if enemy.shoot():
                enemy_bullet = EnemyBullet(enemy.rect.centerx, enemy.rect.bottom)
                self.all_sprites.add(enemy_bullet)
                self.enemy_bullets.add(enemy_bullet)
        
        # Bullet-enemy collision
        hits = pygame.sprite.groupcollide(self.enemies, self.bullets, False, False)
        for enemy in hits:
            for bullet in hits[enemy]:
                bullet.kill()
                enemy.health -= 25
                if enemy.health <= 0:
                    enemy.kill()
                    self.score += 10
                    self.enemies_killed += 1
        
        # Enemy bullet-player collision
        hits = pygame.sprite.spritecollide(self.player, self.enemy_bullets, True)
        self.player.health -= len(hits) * 10
        
        # Enemy-player collision
        hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
        self.player.health -= len(hits) * 0.5
        
        # Check game over
        if self.player.health <= 0:
            self.state = GameState.GAME_OVER
    
    def draw(self):
        """Draw everything"""
        screen.fill(BLACK)
        
        # Draw all sprites
        self.all_sprites.draw(screen)
        
        # Draw health bars
        self.player.draw_health(screen)
        for enemy in self.enemies:
            enemy.draw_health(screen)
        
        # Draw HUD
        score_text = font_small.render(f"Score: {self.score}", True, WHITE)
        wave_text = font_small.render(f"Wave: {self.wave}", True, WHITE)
        health_text = font_small.render(f"Health: {int(self.player.health)}", True, GREEN if self.player.health > 50 else RED)
        enemies_text = font_small.render(f"Enemies: {len(self.enemies)}/{self.max_enemies}", True, WHITE)
        
        screen.blit(score_text, (10, 10))
        screen.blit(wave_text, (10, 50))
        screen.blit(health_text, (SCREEN_WIDTH - 250, 10))
        screen.blit(enemies_text, (SCREEN_WIDTH - 250, 50))
        
        # Draw game over screen
        if self.state == GameState.GAME_OVER:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            game_over_text = font_large.render("GAME OVER", True, RED)
            final_score_text = font_small.render(f"Final Score: {self.score}", True, WHITE)
            final_wave_text = font_small.render(f"Waves Completed: {self.wave - 1}", True, WHITE)
            restart_text = font_small.render("Press R to Restart or Q to Quit", True, YELLOW)
            
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 150))
            screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, 250))
            screen.blit(final_wave_text, (SCREEN_WIDTH // 2 - final_wave_text.get_width() // 2, 300))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 400))
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            clock.tick(FPS)
        
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
