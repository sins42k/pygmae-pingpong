import pygame, sys, os, math, random, time, subprocess
from pygame.locals import *

os.chdir(os.path.dirname(os.path.abspath(__file__)))
pygame.init()
pygame.display.set_caption("중력 모드")
screen = pygame.display.set_mode((1000, 600))
clock = pygame.time.Clock()
main_game_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "main.py")

# 폰트 설정
font = pygame.font.Font(None, 40)
font_large = pygame.font.Font(None, 80)

# 공 이미지를 로드 (이미지 경로 확인 필수)
ball_image = pygame.image.load("image/ball.png").convert_alpha()

# 게임 상태 변수
game_over = False
start_time = time.time()  # 게임 시작 시간 기록
end_time = None           # 게임 오버 시 기록할 시간

# -----------------------------
# 배트 클래스
# -----------------------------
class Bat:
    def __init__(self, ctrls, x, y, width=100, height=10, speed=10):
        self.ctrls = ctrls    # (왼쪽 이동키, 오른쪽 이동키)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed

    def move(self):
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[self.ctrls[0]]:
            self.x -= self.speed
        if pressed_keys[self.ctrls[1]]:
            self.x += self.speed
        # 배트를 맵의 양쪽 끝에 더 가깝게 (여백 5픽셀)
        if self.x < 5:
            self.x = 5
        if self.x + self.width > screen.get_width() - 5:
            self.x = screen.get_width() - self.width - 5

    def draw(self):
        pygame.draw.rect(screen, (255, 255, 255), (self.x, self.y, self.width, self.height))

    def get_rect(self):
        # 판정을 조금 더 관대하게 하기 위해 약간의 여유 영역 추가
        return pygame.Rect(self.x - 10, self.y - 5, self.width + 20, self.height + 10)

# -----------------------------
# 공 클래스 (개선된 충돌 처리)
# -----------------------------
class Ball:
    def __init__(self):
        self.x = screen.get_width() // 2
        self.y = screen.get_height() // 2
        self.speed = 3
        self.dx = random.choice([-2, 2])
        self.dy = random.choice([-5, 5])
        self.collided = False  # 충돌 쿨다운 플래그

    def move(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self):
        screen.blit(ball_image, (int(self.x), int(self.y)))

    def bounce_horizontal(self):
        # 좌우 벽에 닿으면 수평 반사
        if self.x <= 0 and self.dx < 0:
            self.dx *= -1
        if self.x >= screen.get_width() - ball_image.get_width() and self.dx > 0:
            self.dx *= -1

    def bounce(self):
        ball_rect = pygame.Rect(self.x, self.y, ball_image.get_width(), ball_image.get_height())
        top_rect = top_bat.get_rect()
        bottom_rect = bottom_bat.get_rect()

        # 위쪽 배트와의 충돌 (공이 위로 이동 중)
        if self.dy < 0 and top_rect.colliderect(ball_rect):
            if not self.collided:
                self.collided = True
                # 배트 내부에 있는 경우, 배트 바로 아래로 위치 조정
                self.y = top_rect.bottom + 1
                offset = random.uniform(-math.pi/16, math.pi/16)
                new_angle = math.pi/2 + offset  # 90° (즉, 아래로)
                self.speed *= 1.05
                self.dx = math.cos(new_angle) * self.speed
                self.dy = math.sin(new_angle) * self.speed

        # 아래쪽 배트와의 충돌 (공이 아래로 이동 중)
        elif self.dy > 0 and bottom_rect.colliderect(ball_rect):
            if not self.collided:
                self.collided = True
                # 배트 내부에 있는 경우, 배트 바로 위로 위치 조정
                self.y = bottom_rect.top - ball_image.get_height() - 1
                offset = random.uniform(-math.pi/16, math.pi/16)
                new_angle = -math.pi/2 + offset  # -90° (즉, 위로)
                self.speed *= 1.05
                self.dx = math.cos(new_angle) * self.speed
                self.dy = math.sin(new_angle) * self.speed
        else:
            # 충돌 중이 아니면 플래그 초기화
            self.collided = False

# -----------------------------
# 초기 객체 생성
# -----------------------------
# 위쪽 배트: 상단 (y=50)
top_bat = Bat(ctrls=(K_a, K_d), x=450, y=20, width=100, height=10, speed=12)
# 아래쪽 배트: 하단 (y=540)
bottom_bat = Bat(ctrls=(K_LEFT, K_RIGHT), x=450, y=570, width=100, height=10, speed=12)
ball = Ball()

def back_game():
    global ball, game_over, top_bat, bottom_bat, start_time, end_time
    ball = Ball()
    top_bat.x = 450
    bottom_bat.x = 450
    game_over = False
    start_time = time.time()
    end_time = None
    pressed_keys = pygame.key.get_pressed()
    if pressed_keys[pygame.K_SPACE]:
        subprocess.Popen(["python", main_game_path])
        pygame.quit()
        sys.exit()

# -----------------------------
# 메인 게임 루프
# -----------------------------
while True:
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    
    keys = pygame.key.get_pressed()
    
    if game_over:
        if keys[K_SPACE]:
            back_game()
    else:
        top_bat.move()
        bottom_bat.move()
        ball.move()
        ball.bounce_horizontal()
        ball.bounce()
        
        # 공이 화면 상단이나 하단을 벗어나면 게임 오버 처리
        if ball.y < 0 or ball.y > screen.get_height() - ball_image.get_height():
            game_over = True
            end_time = time.time()

    # 경과 시간 계산 (게임 오버 시 end_time 기준)
    current_time = end_time if game_over else time.time()
    elapsed = int(current_time - start_time)
    minutes = elapsed // 60
    seconds = elapsed % 60
    timer_str = f"Time: {minutes:02}:{seconds:02}"
    # 타이머 텍스트를 렌더링한 후 알파값 설정 (.5 투명도)
    time_surface = font.render(timer_str, True, (255, 255, 255))
    time_surface.set_alpha(128)
    # 텍스트를 화면 중앙에 위치
    time_x = (screen.get_width() - time_surface.get_width()) // 2
    time_y = (screen.get_height() - time_surface.get_height()) // 2

    screen.fill((0, 0, 0))
    top_bat.draw()
    bottom_bat.draw()
    ball.draw()
    screen.blit(time_surface, (time_x, time_y))
    
    if game_over:
        over_text = font_large.render("Game Over", True, (255, 0, 0))
        final_time_text = font.render(f"Survived: {minutes:02}:{seconds:02}", True, (255, 255, 255))
        prompt_text = font.render("Press Space to restart", True, (255, 255, 255))
        screen.blit(over_text, ((screen.get_width() - over_text.get_width()) // 2, screen.get_height() // 3))
        screen.blit(final_time_text, ((screen.get_width() - final_time_text.get_width()) // 2, screen.get_height() // 2))
        screen.blit(prompt_text, ((screen.get_width() - prompt_text.get_width()) // 2, screen.get_height() * 2 // 3))
    
    pygame.display.update()
