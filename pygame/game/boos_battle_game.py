import pygame, sys, os, math, random, time
from pygame.locals import *

os.chdir(os.path.dirname(os.path.abspath(__file__)))

pygame.init()
pygame.display.set_caption("Boss Battle Game")
screen = pygame.display.set_mode((1000, 600))
clock = pygame.time.Clock()

# 이미지 로드
ball_image = pygame.image.load("image/ball.png").convert_alpha()

# 색상 정의
colors = [
    (40, 40, 40),  # Light Black (Iron)
    (139, 69, 19), # Brown (Bronze)
    (192, 192, 192), # Silver (Silver)
    (255, 215, 0), # Gold (Gold)
    (135, 206, 250), # Sky Blue (Platinum)
    (0, 255, 0), # Green (Emerald)
    (0, 0, 255), # Blue (Diamond)
    (128, 0, 128), # Purple (Master)
    (255, 0, 0), # Red (Grandmaster)
    (0, 0, 255, 255) # Gold & Blue (Challenger)
]

# 게임 설정
player_health = 3
player_score = 0
boss_health = 5
boss_score = 0

font = pygame.font.Font(None, 40)
font2 = pygame.font.SysFont("corbel", 70)
font3 = pygame.font.Font(None, 60)

# 클래스 정의
class Bat:
    def __init__(self, ctrls, x, side, color, fixed=False):
        self.ctrls = ctrls
        self.x = x
        self.y = 260
        self.side = side
        self.lastbop = 0
        self.color = color
        self.fixed = fixed  # 보스는 고정된 배트

    def move(self):
        if not self.fixed:  # 플레이어만 움직일 수 있게
            if pressed_keys[self.ctrls[0]] and self.y > 0:
                self.y -= 10
            if pressed_keys[self.ctrls[1]] and self.y < 520:
                self.y += 10

    def draw(self):
        offset = -self.side * (time.time() < self.lastbop + 0.05) * 10
        pygame.draw.line(screen, self.color, (self.x + offset, self.y), (self.x + offset, self.y + 80), 6)
        
    def bop(self):
        if time.time() > self.lastbop + 0.3:
            self.lastbop = time.time()

class Ball:
    def __init__(self):
        self.d = (math.pi / 3) * random.random() + (math.pi / 3) + math.pi * random.randint(0, 1)
        self.speed = 12
        self.dx = math.sin(self.d) * self.speed
        self.dy = math.cos(self.d) * self.speed
        self.x = 475
        self.y = 275

    def move(self):
        self.x += self.dx
        self.y += self.dy
    
    def draw(self):
        screen.blit(ball_image, (int(self.x), int(self.y)))

    def bounce(self):
        if (self.y <= 0 and self.dy < 0) or (self.y >= 550 or self.dy > 550):
            self.dy *= -1
            self.d = math.atan2(self.dx, self.dy)
        
        for bat in bats:
            if pygame.Rect(bat.x, bat.y, 6, 80).colliderect((self.x, self.y), ball_image.get_size()) and abs(self.dx) / self.dx == bat.side:
                self.d += random.random() * math.pi / 4 - math.pi / 8
                if (0 < self.d < math.pi / 6) or (math.pi * 5 / 6 < self.d < math.pi):
                    self.d = ((math.pi / 3) * random.random() + (math.pi / 3)) + math.pi
                elif (math.pi < self.d < math.pi * 7 / 6) or (math.pi * 11 / 6 < self.d < math.pi * 2):
                    self.d = ((math.pi / 3) * random.random() + (math.pi / 3)) + math.pi    
                self.d *= -1
                self.d %= math.pi * 2

                if time.time() < bat.lastbop + 0.05 and self.speed < 20:
                    self.speed *= 1.1
                self.dx = math.sin(self.d) * self.speed
                self.dy = math.cos(self.d) * self.speed

# 보스 배트와 플레이어 배트
bats = [Bat([K_w, K_s], 10, -1, colors[0]), Bat([K_UP, K_DOWN], 984, 1, colors[0], fixed=True)]

# 공 초기화
ball = Ball()

# 게임 루프
while True:
    clock.tick(30)
    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_a:
                bats[0].bop()
            if event.key == K_LEFT:
                bats[1].bop()

    pressed_keys = pygame.key.get_pressed()

    # 화면 그리기
    screen.fill((0, 0, 0))
    pygame.draw.line(screen, (255, 255, 255), (screen.get_width() / 2, 0), (screen.get_width() / 2, screen.get_height()), 3)
    pygame.draw.circle(screen, (255, 255, 255), (int(screen.get_width() / 2), int(screen.get_height() / 2)), 50, 3)

    # 플레이어와 보스의 체력 및 점수
    txt = font.render(f"Player HP: {player_health}/3", True, (255, 255, 255))
    screen.blit(txt, (20, 20))

    txt = font.render(f"Boss HP: {boss_health}/5", True, (255, 255, 255))
    screen.blit(txt, (screen.get_width() - 200, 20))

    txt = font.render(f"Player Score: {player_score}", True, (255, 255, 255))
    screen.blit(txt, (20, 60))

    txt = font.render(f"Boss Score: {boss_score}", True, (255, 255, 255))
    screen.blit(txt, (screen.get_width() - 200, 60))

    # 배트 이동 및 그리기
    for bat in bats:
        bat.move()
        bat.draw()

    # 공 이동, 그리기 및 튕기기
    ball.move()
    ball.draw()
    ball.bounce()

    if ball.x < -50:
        ball = Ball()
        player_score += 1
        player_health -= 1  # 플레이어 점수 잃으면 체력 감소

    if ball.x > 1000:
        ball = Ball()
        boss_score += 1
        boss_health -= 1  # 보스 점수 잃으면 체력 감소

    pygame.display.update()
