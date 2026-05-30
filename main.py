import pygame
import sys
import random
import math
import os
import asyncio

# Pygame initialization
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 600
CELL_SIZE = 20
COLS = WIDTH // CELL_SIZE
ROWS = HEIGHT // CELL_SIZE
FPS_START = 10.0
FPS_MAX = 20.0

# Colors
BG_COLOR = (255, 240, 246)       # #fff0f6
GRID_COLOR = (252, 224, 234)     # #fce0ea
SNAKE_COLORS = [
    (244, 192, 209),             # #f4c0d1
    (237, 147, 177),             # #ed93b1
    (224, 96, 144)               # #e06090
]
SNAKE_HEAD_COLOR = (212, 83, 126) # #d4537e
SHIMMER_COLOR = (255, 255, 255)
TEXT_COLOR = (212, 83, 126)
TEXT_SHADOW = (255, 224, 234)

UI_BG_COLOR = (255, 240, 246)
UI_BORDER_COLOR = (237, 147, 177)
POPUP_BG = (255, 224, 234)
POPUP_BORDER = (224, 96, 144)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("snakey babe 🎀")
clock = pygame.time.Clock()

# Fonts
# Attempt to use Segoe UI Emoji for emojis, fallback to standard sans-serif
font_name = "trebuchetms"
try:
    emoji_font_name = "segoeuiemoji"
    pygame.font.SysFont(emoji_font_name, 20)
except:
    emoji_font_name = font_name

try:
    font_path = "assets/Pacifico.ttf"
    font_title = pygame.font.Font(font_path, 48)
    font_large = pygame.font.Font(font_path, 36)
    font_medium = pygame.font.Font(font_path, 24)
    font_small = pygame.font.Font(font_path, 18)
except:
    font_title = pygame.font.SysFont(font_name, 48, bold=True)
    font_large = pygame.font.SysFont(font_name, 36, bold=True)
    font_medium = pygame.font.SysFont(font_name, 24, bold=True)
    font_small = pygame.font.SysFont(font_name, 18, bold=True)

font_emoji_large = pygame.font.SysFont(emoji_font_name, 48)
font_emoji_medium = pygame.font.SysFont(emoji_font_name, 24)

# Load Best Score
BEST_SCORE_FILE = "best_score.txt"
best_score = 0
if os.path.exists(BEST_SCORE_FILE):
    try:
        with open(BEST_SCORE_FILE, "r") as f:
            best_score = int(f.read().strip())
    except:
        pass

def save_best_score(score):
    global best_score
    if score > best_score:
        best_score = score
        try:
            with open(BEST_SCORE_FILE, "w") as f:
                f.write(str(best_score))
        except:
            pass

def draw_text(surface, text, font, color, center_x, center_y, shadow=False):
    if shadow:
        shadow_surface = font.render(text, True, TEXT_SHADOW)
        shadow_rect = shadow_surface.get_rect(center=(center_x + 2, center_y + 2))
        surface.blit(shadow_surface, shadow_rect)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(center_x, center_y))
    surface.blit(text_surface, text_rect)

def rounded_rect(surface, color, rect, radius, width=0):
    pygame.draw.rect(surface, color, rect, border_radius=radius, width=width)

def draw_strawberry(surface, x, y, size):
    # Strawberry body
    body_points = [
        (x + size/2, y + size),
        (x + size*0.1, y + size*0.6),
        (x + size*0.1, y + size*0.3),
        (x + size/2, y + size*0.1),
        (x + size*0.9, y + size*0.3),
        (x + size*0.9, y + size*0.6)
    ]
    pygame.draw.polygon(surface, (245, 50, 90), body_points)
    
    # Seeds
    seed_color = (255, 230, 120)
    pygame.draw.circle(surface, seed_color, (int(x + size*0.3), int(y + size*0.4)), 1)
    pygame.draw.circle(surface, seed_color, (int(x + size*0.7), int(y + size*0.4)), 1)
    pygame.draw.circle(surface, seed_color, (int(x + size*0.5), int(y + size*0.6)), 1)
    pygame.draw.circle(surface, seed_color, (int(x + size*0.3), int(y + size*0.7)), 1)
    pygame.draw.circle(surface, seed_color, (int(x + size*0.7), int(y + size*0.7)), 1)
    pygame.draw.circle(surface, seed_color, (int(x + size*0.5), int(y + size*0.8)), 1)
    
    # Leaf
    leaf_points = [
        (x + size/2, y + size*0.25),
        (x + size*0.15, y),
        (x + size*0.35, y + size*0.15),
        (x + size/2, y - size*0.05),
        (x + size*0.65, y + size*0.15),
        (x + size*0.85, y)
    ]
    pygame.draw.polygon(surface, (80, 210, 100), leaf_points)

def draw_ribbon(surface, center_x, center_y, size, angle_deg):
    ribbon_surf = pygame.Surface((size, size), pygame.SRCALPHA)
    
    rc = (255, 105, 180) # Pink bow
    # Left loop
    pygame.draw.polygon(ribbon_surf, rc, [(size/2, size/2), (0, size*0.2), (0, size*0.8)])
    # Right loop
    pygame.draw.polygon(ribbon_surf, rc, [(size/2, size/2), (size, size*0.2), (size, size*0.8)])
    # Center knot
    pygame.draw.circle(ribbon_surf, (255, 20, 147), (int(size/2), int(size/2)), int(size*0.25))
    
    rotated = pygame.transform.rotate(ribbon_surf, angle_deg)
    rect = rotated.get_rect(center=(center_x, center_y))
    surface.blit(rotated, rect)

def draw_crown(surface, x, y, size):
    gold = (255, 215, 0)
    points = [
        (x, y + size),
        (x, y + size*0.4),
        (x + size*0.25, y + size*0.7),
        (x + size*0.5, y + size*0.1),
        (x + size*0.75, y + size*0.7),
        (x + size, y + size*0.4),
        (x + size, y + size)
    ]
    pygame.draw.polygon(surface, gold, points)
    # Jewels
    pygame.draw.circle(surface, (255, 50, 100), (int(x), int(y + size*0.4)), 3)
    pygame.draw.circle(surface, (50, 150, 255), (int(x + size*0.5), int(y + size*0.1)), 4)
    pygame.draw.circle(surface, (255, 50, 100), (int(x + size), int(y + size*0.4)), 3)

class Sparkle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.life = 20
        self.max_life = 20
    
    def draw(self, surface):
        if self.life > 0:
            alpha = int((self.life / self.max_life) * 255)
            size = int(CELL_SIZE * 1.5 * (1 - self.life / self.max_life))
            
            s = pygame.Surface((size, size), pygame.SRCALPHA)
            color = (255, 230, 150, alpha)
            center = size // 2
            pygame.draw.line(s, color, (center, 0), (center, size), 2)
            pygame.draw.line(s, color, (0, center), (size, center), 2)
            pygame.draw.circle(s, color, (center, center), 2)
            
            rect = s.get_rect(center=(self.x, self.y))
            surface.blit(s, rect)

class Game:
    def __init__(self):
        self.reset()
        self.state = "START" # START, PLAYING, PAUSED, GAMEOVER
        
    def reset(self):
        self.snake = [(COLS//2, ROWS//2), (COLS//2 - 1, ROWS//2), (COLS//2 - 2, ROWS//2)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.food = self.spawn_food()
        self.score = 0
        self.fps = FPS_START
        self.sparkles = []
        
    def spawn_food(self):
        while True:
            food = (random.randint(0, COLS-1), random.randint(0, ROWS-1))
            if food not in self.snake:
                return food

    def update(self):
        if self.state != "PLAYING":
            return
            
        self.direction = self.next_direction
        
        head_x, head_y = self.snake[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)
        
        # Check collision with walls
        if new_head[0] < 0 or new_head[0] >= COLS or new_head[1] < 0 or new_head[1] >= ROWS:
            self.game_over()
            return
            
        # Check collision with self
        if new_head in self.snake:
            self.game_over()
            return
            
        self.snake.insert(0, new_head)
        
        if new_head == self.food:
            self.score += 1
            if self.score % 5 == 0 and self.fps < FPS_MAX:
                self.fps += 0.5
            self.sparkles.append(Sparkle(self.food[0] * CELL_SIZE + CELL_SIZE//2, self.food[1] * CELL_SIZE + CELL_SIZE//2))
            self.food = self.spawn_food()
        else:
            self.snake.pop()
            
        # Update sparkles
        for s in self.sparkles[:]:
            s.life -= 1
            if s.life <= 0:
                self.sparkles.remove(s)

    def game_over(self):
        self.state = "GAMEOVER"
        save_best_score(self.score)

    def draw(self, surface):
        surface.fill(BG_COLOR)
        
        # Draw grid
        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL_SIZE):
            pygame.draw.line(surface, GRID_COLOR, (0, y), (WIDTH, y))
            
        # Draw Food
        fx, fy = self.food
        draw_strawberry(surface, fx * CELL_SIZE, fy * CELL_SIZE, CELL_SIZE)
        
        # Draw Snake
        for i, (sx, sy) in enumerate(reversed(self.snake)):
            px = sx * CELL_SIZE
            py = sy * CELL_SIZE
            real_index = len(self.snake) - 1 - i
            
            if real_index == 0:
                # Head
                rect = (px, py, CELL_SIZE, CELL_SIZE)
                rounded_rect(surface, SNAKE_HEAD_COLOR, rect, 6)
                
                # Eyes
                eye_radius = 3
                pupil_radius = 1.5
                if self.direction == (1, 0) or self.direction == (-1, 0):
                    e1_pos = (px + CELL_SIZE*0.7 if self.direction[0]==1 else px + CELL_SIZE*0.3, py + CELL_SIZE*0.3)
                    e2_pos = (px + CELL_SIZE*0.7 if self.direction[0]==1 else px + CELL_SIZE*0.3, py + CELL_SIZE*0.7)
                else:
                    e1_pos = (px + CELL_SIZE*0.3, py + CELL_SIZE*0.7 if self.direction[1]==1 else py + CELL_SIZE*0.3)
                    e2_pos = (px + CELL_SIZE*0.7, py + CELL_SIZE*0.7 if self.direction[1]==1 else py + CELL_SIZE*0.3)
                    
                pygame.draw.circle(surface, (255, 255, 255), (int(e1_pos[0]), int(e1_pos[1])), eye_radius)
                pygame.draw.circle(surface, (255, 255, 255), (int(e2_pos[0]), int(e2_pos[1])), eye_radius)
                pygame.draw.circle(surface, (0, 0, 0), (int(e1_pos[0]), int(e1_pos[1])), int(pupil_radius))
                pygame.draw.circle(surface, (0, 0, 0), (int(e2_pos[0]), int(e2_pos[1])), int(pupil_radius))
                
                # Ribbon
                angle = 0
                if self.direction == (0, -1): angle = 90
                elif self.direction == (-1, 0): angle = 180
                elif self.direction == (0, 1): angle = 270
                
                draw_ribbon(surface, px + CELL_SIZE/2, py + CELL_SIZE/2, CELL_SIZE*0.8, angle)
                
            else:
                # Body
                color = SNAKE_COLORS[real_index % len(SNAKE_COLORS)]
                rect = (px + 1, py + 1, CELL_SIZE - 2, CELL_SIZE - 2)
                rounded_rect(surface, color, rect, 5)
                # Shimmer dot
                pygame.draw.circle(surface, SHIMMER_COLOR, (px + 6, py + 6), 2)
                
        # Draw Sparkles
        for s in self.sparkles:
            s.draw(surface)

        # Draw UI
        if self.state == "PLAYING":
            # Score pills
            score_text = f" score: {self.score} "
            best_text = f" best: {max(self.score, best_score)} "
            
            s_surf = font_medium.render(score_text, True, TEXT_COLOR)
            b_surf = font_medium.render(best_text, True, TEXT_COLOR)
            
            s_rect = s_surf.get_rect(topleft=(20, 20))
            b_rect = b_surf.get_rect(topright=(WIDTH - 20, 20))
            
            # Pill background for score
            bg_rect_s = s_rect.inflate(20, 10)
            rounded_rect(surface, UI_BG_COLOR, bg_rect_s, 15)
            rounded_rect(surface, UI_BORDER_COLOR, bg_rect_s, 15, 2)
            surface.blit(s_surf, s_rect)
            
            # Pill background for best score
            bg_rect_b = b_rect.inflate(20, 10)
            rounded_rect(surface, UI_BG_COLOR, bg_rect_b, 15)
            rounded_rect(surface, UI_BORDER_COLOR, bg_rect_b, 15, 2)
            surface.blit(b_surf, b_rect)
            
            # Fun message
            msg = "go girl! 💖" if self.score > 0 else "you got this! 💕"
            draw_text(surface, msg, font_medium, TEXT_COLOR, WIDTH//2, HEIGHT - 30, shadow=True)
            
            # Title top center
            draw_text(surface, "snakey babe 🎀", font_medium, TEXT_COLOR, WIDTH//2, 35, shadow=True)

        elif self.state == "START":
            # Overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 240, 246, 180))
            surface.blit(overlay, (0,0))
            
            draw_text(surface, "snakey babe 🎀", font_title, TEXT_COLOR, WIDTH//2, HEIGHT//2 - 100, shadow=True)
            
            # Pulse logic for "press SPACE"
            pulse = math.sin(pygame.time.get_ticks() / 200.0) * 10
            draw_text(surface, "press SPACE to play 💕", font_medium, TEXT_COLOR, WIDTH//2, HEIGHT//2 - 20 + pulse)
            
            # Tutorial text
            t_color = (224, 96, 144)
            draw_text(surface, "How to play:", font_medium, t_color, WIDTH//2, HEIGHT//2 + 60)
            draw_text(surface, "use arrow keys to move 🎀", font_small, t_color, WIDTH//2, HEIGHT//2 + 90)
            draw_text(surface, "eat strawberries 🍓 to grow", font_small, t_color, WIDTH//2, HEIGHT//2 + 115)
            draw_text(surface, "don't hit walls or yourself 💕", font_small, t_color, WIDTH//2, HEIGHT//2 + 140)
            
        elif self.state == "PAUSED":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 240, 246, 180))
            surface.blit(overlay, (0,0))
            
            draw_text(surface, "paused 🎀", font_title, TEXT_COLOR, WIDTH//2, HEIGHT//2 - 30, shadow=True)
            draw_text(surface, "press SPACE to resume", font_medium, TEXT_COLOR, WIDTH//2, HEIGHT//2 + 30)
            
        elif self.state == "GAMEOVER":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 240, 246, 200))
            surface.blit(overlay, (0,0))
            
            # Popup card
            card_w, card_h = 350, 300
            card_rect = pygame.Rect(WIDTH//2 - card_w//2, HEIGHT//2 - card_h//2, card_w, card_h)
            rounded_rect(surface, POPUP_BG, card_rect, 20)
            rounded_rect(surface, POPUP_BORDER, card_rect, 20, 4)
            
            draw_crown(surface, WIDTH//2 - 25, HEIGHT//2 - 120, 50)
            
            draw_text(surface, "game over!", font_large, TEXT_COLOR, WIDTH//2, HEIGHT//2 - 40, shadow=True)
            draw_text(surface, f"score: {self.score}", font_large, TEXT_COLOR, WIDTH//2, HEIGHT//2 + 10)
            draw_text(surface, f"best: {best_score}", font_medium, TEXT_COLOR, WIDTH//2, HEIGHT//2 + 60)
            
            draw_text(surface, "play again? press SPACE 💖", font_small, TEXT_COLOR, WIDTH//2, HEIGHT//2 + 110)

async def main():
    game = Game()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game.state == "START" or game.state == "GAMEOVER":
                        game.reset()
                        game.state = "PLAYING"
                    elif game.state == "PLAYING":
                        game.state = "PAUSED"
                    elif game.state == "PAUSED":
                        game.state = "PLAYING"
                        
                if game.state == "PLAYING":
                    if event.key == pygame.K_UP and game.direction != (0, 1):
                        game.next_direction = (0, -1)
                    elif event.key == pygame.K_DOWN and game.direction != (0, -1):
                        game.next_direction = (0, 1)
                    elif event.key == pygame.K_LEFT and game.direction != (1, 0):
                        game.next_direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT and game.direction != (-1, 0):
                        game.next_direction = (1, 0)
                        
        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(game.fps if game.state == "PLAYING" else 15)
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())
