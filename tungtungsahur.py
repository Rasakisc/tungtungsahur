import pygame
import sys
import random
import math

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1000, 700
WORLD_WIDTH, WORLD_HEIGHT = 4000, 4000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lari dari Tung tung sahur (Versi PBO Final)")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
RED = (255, 50, 50)
BLACK = (0, 0, 0)
GREEN = (50, 200, 50)
DARK_GRAY = (40, 40, 40)

font = pygame.font.SysFont(None, 64)
small_font = pygame.font.SysFont(None, 36)

ai_sound = pygame.mixer.Sound("tungsuara.mp3") 
ai_sound.play(loops=-1)
ai_sound.set_volume(0)

player_size, ai_size = 80, 80
raw_player = pygame.image.load("rasaki.png").convert_alpha() 
player_img = pygame.transform.scale(raw_player, (player_size, player_size))

raw_ai = pygame.image.load("tungkarak.png").convert_alpha()
ai_img = pygame.transform.scale(raw_ai, (ai_size, ai_size))


class Entitas:
    def __init__(self, x, y, size, img):
        self.x = x
        self.y = y
        self.size = size
        self.img = img
        self.facing_right = True
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)

    def update_hitbox(self):
        self.rect.x = self.x
        self.rect.y = self.y

    def draw(self, surface, cam_x, cam_y):
        draw_x = self.x - cam_x
        draw_y = self.y - cam_y
        
        if self.facing_right:
            surface.blit(self.img, (draw_x, draw_y))
        else:
            flipped_img = pygame.transform.flip(self.img, True, False)
            surface.blit(flipped_img, (draw_x, draw_y))

class Pemain(Entitas):
    def __init__(self, x, y, size, img):
        super().__init__(x, y, size, img)
        self.stamina = 100.0
        self.normal_speed = 5
        self.sprint_speed = 9

    def bergerak(self, keys):
        current_speed = self.normal_speed
        
        if keys[pygame.K_LSHIFT] and self.stamina > 0:
            current_speed = self.sprint_speed
            self.stamina -= 1
        elif self.stamina < 100:
            self.stamina += 0.5

        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.x > 0: 
            self.x -= current_speed
            self.facing_right = False
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.x < WORLD_WIDTH - self.size: 
            self.x += current_speed
            self.facing_right = True
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.y > 0: 
            self.y -= current_speed
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.y < WORLD_HEIGHT - self.size: 
            self.y += current_speed
            
        self.update_hitbox()

class Musuh(Entitas):
    def __init__(self, x, y, size, img, speed):
        super().__init__(x, y, size, img)
        self.speed = speed

    def kejar(self, target_x, target_y):
        if self.x < target_x: 
            self.x += self.speed
            self.facing_right = False
        elif self.x > target_x: 
            self.x -= self.speed
            self.facing_right = True
            
        if self.y < target_y: self.y += self.speed
        elif self.y > target_y: self.y -= self.speed
        
        self.update_hitbox()


def main():
    player = Pemain(WORLD_WIDTH // 2, WORLD_HEIGHT // 2, player_size, player_img)
    enemies = [Musuh(100, 100, ai_size, ai_img, 4)]
    
    start_time = pygame.time.get_ticks()
    last_spawn_time = start_time
    SPAWN_INTERVAL = 5000
    game_over = False
    running = True

    while running:
        current_time = pygame.time.get_ticks()
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not game_over:
            survival_time = (current_time - start_time) // 1000
            
            if current_time - last_spawn_time > SPAWN_INTERVAL:
                spawn_x = random.randint(0, WORLD_WIDTH - ai_size)
                spawn_y = random.randint(0, WORLD_HEIGHT - ai_size)
                enemies.append(Musuh(spawn_x, spawn_y, ai_size, ai_img, 4))
                last_spawn_time = current_time

            keys = pygame.key.get_pressed()
            player.bergerak(keys)

            camera_x = player.x - WIDTH // 2 + player.size // 2
            camera_y = player.y - HEIGHT // 2 + player.size // 2

            min_distance = float('inf')
            hitbox_player = player.rect.inflate(-20, -20)
            
            for enemy in enemies:
                enemy.kejar(player.x, player.y)
                
                dist = math.hypot(enemy.x - player.x, enemy.y - player.y)
                if dist < min_distance: 
                    min_distance = dist
                
                hitbox_enemy = enemy.rect.inflate(-20, -20)
                if hitbox_player.colliderect(hitbox_enemy):
                    game_over = True
                    ai_sound.set_volume(0) # Suara langsung mati saat tertangkap

            if not game_over:
                max_hear_distance = 600.0
                volume = 1.0 - (min_distance / max_hear_distance) 
                if volume < 0: volume = 0.0
                ai_sound.set_volume(volume)

        # --- RENDER ---
        screen.fill(DARK_GRAY) 

        if not game_over:
            map_rect = pygame.Rect(-camera_x, -camera_y, WORLD_WIDTH, WORLD_HEIGHT)
            pygame.draw.rect(screen, "#7E7E7E", map_rect)
            pygame.draw.rect(screen, BLACK, map_rect, 10) 

            for enemy in enemies:
                enemy.draw(screen, camera_x, camera_y)
            player.draw(screen, camera_x, camera_y)

            time_text = font.render(f"{survival_time} dtk", True, BLACK)
            screen.blit(time_text, (WIDTH // 2 - time_text.get_width() // 2, 20))
            
            ai_count_text = small_font.render(f"Jumlah AI: {len(enemies)}", True, RED)
            screen.blit(ai_count_text, (10, 10))

            pygame.draw.rect(screen, BLACK, (10, HEIGHT - 35, 204, 24), 2)
            pygame.draw.rect(screen, GREEN, (12, HEIGHT - 33, player.stamina * 2, 20))

        else:
            text_go = font.render("GAME OVER!", True, WHITE)
            text_score = font.render(f"Bertahan: {survival_time} Detik", True, RED)
            text_restart = small_font.render("tekan 'r' untuk main lagi atau 'esc' untuk keluar", True, WHITE)
            
            screen.blit(text_go, (WIDTH//2 - text_go.get_width()//2, HEIGHT//2 - 80))
            screen.blit(text_score, (WIDTH//2 - text_score.get_width()//2, HEIGHT//2 - 10))
            screen.blit(text_restart, (WIDTH//2 - text_restart.get_width()//2, HEIGHT//2 + 60))
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]: 
                main()
                return
            elif keys[pygame.K_ESCAPE]: 
                running = False

        pygame.display.flip()

    ai_sound.stop()
    pygame.quit()
    sys.exit()

