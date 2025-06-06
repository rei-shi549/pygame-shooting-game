import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("中級Step5: 攻撃機能追加")
clock = pygame.time.Clock()

# フォント
font_big = pygame.font.Font(None, 80)
font_small = pygame.font.Font(None, 36)

# --- クラス定義（同じ） ---
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 40
        self.color = (0, 128, 255)
        self.speed = 5
        self.hp = 300

    def move(self, keys):
        if keys[pygame.K_LEFT]: self.x -= self.speed
        if keys[pygame.K_RIGHT]: self.x += self.speed
        if keys[pygame.K_UP]: self.y -= self.speed
        if keys[pygame.K_DOWN]: self.y += self.speed
        self.x = max(0, min(self.x, WIDTH - self.size))
        self.y = max(0, min(self.y, HEIGHT - self.size))

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

class BaseEnemy:
    def __init__(self, x, y, speed, color, hp):
        self.x = x
        self.y = y
        self.size = 40
        self.speed_x = speed
        self.speed_y = speed
        self.color = color
        self.hp = hp

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y
        if self.x < 0 or self.x > WIDTH - self.size:
            self.speed_x *= -1
        if self.y < 0 or self.y > HEIGHT - self.size:
            self.speed_y *= -1

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)
    
class RedEnemy(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y, speed=5, color=(255, 0, 0), hp=1)
        
class BlueEnemy(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y, speed=2, color=(0, 0, 255), hp=5)

class GreenEnemy(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y, speed=2, color=(0, 255, 0), hp=2)

    def move(self):
        # 時々ランダムな方向転換
        if random.random() < 0.05:  # 5%の確率で方向を変える
            self.speed_x = random.choice([-2, -1, 1, 2])
            self.speed_y = random.choice([-2, -1, 1, 2])

        self.x += self.speed_x
        self.y += self.speed_y

        # 画面内に強制的に留める
        if self.x < 0:
            self.x = 0
            self.speed_x *= -1
        if self.x > WIDTH - self.size:
            self.x = WIDTH - self.size
            self.speed_x *= -1
        if self.y < 0:
            self.y = 0
            self.speed_y *= -1
        if self.y > HEIGHT - self.size:
            self.y = HEIGHT - self.size
            self.speed_y *= -1
class BossEnemy:
    def __init__(self):
        self.x = WIDTH // 2 - 50
        self.y = 50
        self.width = 100
        self.height = 100
        self.base_color = (128, 0, 128)  # 通常時の紫色
        self.color = self.base_color
        self.speed_x = 2
        self.hp = 30
        self.flash_timer = 0  # ★点滅タイマー
        
    def move(self):
        self.x += self.speed_x
        if self.x < 0 or self.x > WIDTH - self.width:
            self.speed_x *= -1

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


# --- 追加：ビームクラス ---
class Beam:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 5
        self.height = 10
        self.color = (0, 0, 255)
        self.speed = 10

    def move(self):
        self.y -= self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
class HitEffect:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.timer = 10  # フレーム数（数フレームで消える）

    def update(self):
        self.timer -= 1
        self.radius += 1  # 少しずつ膨らむ

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 0, 0), (self.x, self.y), self.radius)

class BossBeam:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 8
        self.height = 16
        self.color = (255, 0, 0)  # 赤い弾
        self.speed = 5

    def move(self):
        self.y += self.speed  # 下方向に飛ぶ

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

def spawn_enemies(wave, player=None):
    enemies = []
    for _ in range(wave * 2):
        while True:
            enemy_type = random.choice(["red", "green", "blue"]) if wave >= 3 else "red"
            x = random.randint(0, WIDTH - 50)
            y = random.randint(0, HEIGHT - 40)

            # プレイヤーと距離が離れているかチェック
            if player:
                distance = ((player.x - x)**2 + (player.y - y)**2)**0.5
                if distance < 100:  # 100px以内なら再抽選
                    continue

            if enemy_type == "red":
                enemies.append(RedEnemy(x, y))
            elif enemy_type == "green":
                enemies.append(GreenEnemy(x, y))
            else:
                enemies.append(BlueEnemy(x, y))
            break
    return enemies


# --- 初期化関数 ---
def init_game():
    player = Player(100, 200)
    enemies = spawn_enemies(1)  # ← ここでWave1用の敵を出す！
    return player, enemies, 3000, 0

# --- Game Over画面 ---
def show_game_over():
    screen.fill((255, 255, 255))
    text = font_big.render("Game Over", True, (255, 0, 0))
    screen.blit(text, text.get_rect(center=(WIDTH//2, HEIGHT//2 - 60)))

    retry_text = font_small.render("Retry", True, (255, 255, 255))
    retry_rect = pygame.Rect(WIDTH//2 - 60, HEIGHT//2 + 20, 120, 50)
    pygame.draw.rect(screen, (0, 128, 0), retry_rect)  # ボタン
    screen.blit(retry_text, retry_text.get_rect(center=retry_rect.center))
    pygame.display.flip()
    return retry_rect

def show_result(score, red_cnt, green_cnt, blue_cnt):
    screen.fill((255, 255, 255))
    
    text = font_big.render("You Win!", True, (0, 128, 0))
    screen.blit(text, text.get_rect(center=(WIDTH//2, HEIGHT//2 - 100)))

    score_text = font_small.render(f"Final Score: {score}", True, (0, 0, 0))
    screen.blit(score_text, score_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 30)))

    # ★ここから追加！
    red_text = font_small.render(f"Red Enemies: {red_cnt}", True, (255, 0, 0))
    screen.blit(red_text, red_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 10)))

    green_text = font_small.render(f"Green Enemies: {green_cnt}", True, (0, 128, 0))
    screen.blit(green_text, green_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 40)))

    blue_text = font_small.render(f"Blue Enemies: {blue_cnt}", True, (0, 0, 255))
    screen.blit(blue_text, blue_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 70)))

    quit_text = font_small.render("Click to Exit", True, (0, 0, 0))
    screen.blit(quit_text, quit_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 110)))

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.MOUSEBUTTONDOWN:
                pygame.quit()
                sys.exit()

def show_boss_result(score, wave):
    screen.fill((255, 255, 255))
    text = font_big.render("Boss Defeated!", True, (255, 0, 255))
    screen.blit(text, text.get_rect(center=(WIDTH//2, HEIGHT//2 - 80)))

    score_text = font_small.render(f"Final Score: {score}", True, (0, 0, 0))
    screen.blit(score_text, score_text.get_rect(center=(WIDTH//2, HEIGHT//2)))

    wave_text = font_small.render(f"Cleared Waves: {wave-1}", True, (0, 0, 0))
    screen.blit(wave_text, wave_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 40)))

    quit_text = font_small.render("Click to Exit", True, (0, 0, 0))
    screen.blit(quit_text, quit_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 100)))

    pygame.display.flip()    

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.MOUSEBUTTONDOWN:
                pygame.quit()
                sys.exit()

# --- メインループ ---
def main_loop():
    boss = None  # 最初は登場していない
    boss_spawned = False  # ボス出現フラグ
    player, enemies, score, damage_cooldown = init_game()
    beams = []  # ビームリストを追加
    boss_beams = []
    running = True
    effects = []  # ヒットエフェクトのリスト
    blue_cnt = 0
    red_cnt = 0
    green_cnt = 0
    wave = 0
    wave_clear = True
    wave_clear_timer = 0
    boss = None
    boss_spawned = False
    
    while running:
        dt = clock.tick(60)
        score -= dt // (1000 // 60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # ビームを発射（プレイヤーの中心から）
                    beam_x = player.x + player.size // 2 - 2
                    beam_y = player.y
                    beams.append(Beam(beam_x, beam_y))

        keys = pygame.key.get_pressed()
        player.move(keys)

        screen.fill((255, 255, 255))

        # ビームの移動＆描画
        for beam in beams[:]:
            beam.move()
            beam.draw(screen)
            if beam.y < 0:
                beams.remove(beam)

        # 敵処理
        for enemy in enemies[:]:
            enemy.move()
            enemy.draw(screen)

        # ビームと敵の当たり判定
        for beam in beams[:]:
            for enemy in enemies[:]:
                if beam.get_rect().colliderect(enemy.get_rect()):
                    enemy.hp -= 1
                    beams.remove(beam)
                    effects.append(HitEffect(enemy.x + enemy.size // 2, enemy.y + enemy.size // 2))
                    if enemy.hp <= 0:
                        enemies.remove(enemy)
                        if enemy.color == (255,0,0):
                            score += 200
                            red_cnt +=1
                        elif enemy.color == (0,255,0):
                            score += 500
                            green_cnt += 1
                        elif enemy.color == (0,0,255):
                            score += 1000
                            blue_cnt += 1
                    break
                
        if not wave_clear and not enemies and not boss_spawned:
            wave += 1
            wave_clear = True
            wave_clear_timer = 120  # 2秒間（60FPS換算）

        if wave_clear:
            if wave <= 5:
                text = font_big.render(f"Wave {wave}!", True, (0, 128, 0))
            else:
                text = font_big.render("Emergency!", True, (255, 0, 0))
            screen.blit(text, text.get_rect(center=(WIDTH//2, HEIGHT//2)))
            wave_clear_timer -= 1
            if wave_clear_timer <= 0:
                if wave <= 5:
                    enemies = spawn_enemies(wave)
                    wave_clear = False
                else:
                    boss = BossEnemy()
                    boss_spawned = True
                    wave_clear = False

        # プレイヤーと敵の接触判定
        if damage_cooldown <= 0:
            for enemy in enemies:
                if player.get_rect().colliderect(enemy.get_rect()):
                    player.hp -= 1
                    damage_cooldown = 60
                    break
        else:
            damage_cooldown -= 1

        # ビームとボスの当たり判定
        if boss:
            # フラッシュ中なら色を白黒に
            if boss.flash_timer > 0:
                if boss.flash_timer % 4 < 2:  # 交互に
                    boss.color = (255, 255, 255)  # 白
                else:
                    boss.color = (0, 0, 0)  # 黒
                boss.flash_timer -= 1
            else: 
                boss.color = boss.base_color  # 通常色に戻す
                
            boss.move()
            boss.draw(screen)

            for beam in beams[:]:
                if beam.get_rect().colliderect(boss.get_rect()):
                    boss.hp -= 1
                    boss.width -= 2
                    boss.height -= 2
                    boss.flash_timer = 10  # ★10フレーム点滅
                    beams.remove(beam)
                    effects.append(HitEffect(boss.x + boss.width // 2, boss.y + boss.height // 2))
                    if boss.hp <= 15 and abs(boss.speed_x) == 2:
                        boss.speed_x *= 3
            if boss.hp <= 0:
                show_boss_result(score,wave)  # 勝利画面へ
        # ボスHPバー表示
        if boss:
            hp_bar_width = 200
            hp_ratio = boss.hp / 30  # 30はボスの最大HP
            hp_bar_color = (255, 0, 0)
            pygame.draw.rect(screen, (128, 128, 128), (WIDTH//2 - hp_bar_width//2, 10, hp_bar_width, 20))  # 背景
            pygame.draw.rect(screen, hp_bar_color, (WIDTH//2 - hp_bar_width//2, 10, int(hp_bar_width * hp_ratio), 20))  # 現在のHP

        # ボスの攻撃（ランダムに弾を発射）
        if boss and random.random() < 0.02:  # 2%の確率で発射
            beam_x = random.randint(boss.x , boss.x + boss.width) 
            beam_y = boss.y + boss.height
            boss_beams.append(BossBeam(beam_x, beam_y))
            
        for boss_beam in boss_beams[:]:
            boss_beam.move()
            boss_beam.draw(screen)
            if boss_beam.y > HEIGHT:
                boss_beams.remove(boss_beam)

            if player.get_rect().colliderect(boss_beam.get_rect()):
                player.hp -= 1
                boss_beams.remove(boss_beam)


        # Game Over画面
        if player.hp <= 0:
            retry_rect = show_game_over()
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if retry_rect.collidepoint(event.pos):
                            waiting = False
                            player, enemies, score, damage_cooldown = init_game()
                            beams.clear()
                            boss = None
                            boss_spawned = False
                            boss_beams.clear()
                            wave = 1
    
        # UI表示
        hp_text = font_small.render(f"HP: {player.hp}", True, (0, 0, 0))
        screen.blit(hp_text, (10, 10))
        score_text = font_small.render(f"Score: {score:04}", True, (0, 0, 0))
        screen.blit(score_text, (10, 40))

        for effect in effects[:]:
            effect.update()
            effect.draw(screen)
            if effect.timer <= 0:
                effects.remove(effect)

        player.draw(screen)
        pygame.display.flip()

# ゲームスタート
main_loop()
