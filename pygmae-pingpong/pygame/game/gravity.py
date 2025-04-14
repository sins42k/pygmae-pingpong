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

# 배트 색상 관련 설정 (색상명과 RGB 값)
bat_colors = {
    "green": (0, 255, 0),
    "red": (255, 0, 0),
    "purple": (128, 0, 128),
    "yellow": (255, 255, 0)
}
possible_colors = list(bat_colors.keys())

# 공 이미지 딕셔너리: 각 색상별 공 이미지를 미리 로드
ball_images = {}
for color in ["green", "red", "purple", "yellow"]:
    # 파일 경로는 "image/{색상}_character.png" 형태로 가정합니다.
    ball_images[color] = pygame.image.load(f"image/{color}_character.png").convert_alpha()

# 기본 공 이미지(초기 상태는 노란색)
# (이제 공 클래스 내부에서 ball_images["yellow"]를 사용합니다)

# 게임 상태 변수
game_over = False
start_time = time.time()  # 게임 시작 시간 기록
end_time = None           # 게임 오버 시 기록할 시간

# -----------------------------
# 배트 클래스
# -----------------------------
class Bat:
    def __init__(self, ctrls, x, y, width=100, height=10, speed=10, color_key="yellow"):
        self.ctrls = ctrls    # (왼쪽 이동키, 오른쪽 이동키)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.color_name = color_key  # 색상 이름 (예: "red")
        self.color = bat_colors[color_key]  # RGB 값

    def move(self):
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[self.ctrls[0]]:
            self.x -= self.speed
        if pressed_keys[self.ctrls[1]]:
            self.x += self.speed
        # 배트를 맵 양쪽 끝에 5픽셀 여백 유지
        if self.x < 5:
            self.x = 5
        if self.x + self.width > screen.get_width() - 5:
            self.x = screen.get_width() - self.width - 5

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def get_rect(self):
        # 충돌 판정을 위해 약간의 여유 영역 추가
        return pygame.Rect(self.x - 10, self.y - 5, self.width + 20, self.height + 10)

# -----------------------------
# 공 클래스 (개선된 충돌 처리 및 배트 색상 반영)
# -----------------------------
class Ball:
    def __init__(self):
        self.x = screen.get_width() // 2
        self.y = screen.get_height() // 2
        self.speed = 3
        self.dx = random.choice([-2, 2])
        self.dy = random.choice([-5, 5])
        self.collided = False  # 충돌 쿨다운 플래그
        # 초기 공 이미지는 노란색
        self.image = ball_images["yellow"]

    def move(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self):
        screen.blit(self.image, (int(self.x), int(self.y)))

    def bounce_horizontal(self):
        # 좌우 벽에 닿으면 수평 반사 (자신의 이미지 크기를 사용)
        if self.x <= 0 and self.dx < 0:
            self.dx *= -1
        if self.x >= screen.get_width() - self.image.get_width() and self.dx > 0:
            self.dx *= -1

    def bounce(self):
    # 기존 공의 Rect보다 10픽셀씩 축소한 충돌 영역 사용
        ball_rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        ball_rect = ball_rect.inflate(-30, -30)  # 좌우, 상하 각각 10픽셀 축소

        top_rect = top_bat.get_rect()
        bottom_rect = bottom_bat.get_rect()

        # 위쪽 배트와의 충돌 (공이 위로 이동 중)
        if self.dy < 0 and top_rect.colliderect(ball_rect):
            if not self.collided:
                self.collided = True
                # 배트 내부에 있을 경우, 배트 바로 아래로 위치 조정
                self.y = top_rect.bottom + 1
                offset = random.uniform(-math.pi/16, math.pi/16)
                new_angle = math.pi/2 + offset  # 90° (즉, 아래로)
                self.speed *= 1.05
                self.dx = math.cos(new_angle) * self.speed
                self.dy = math.sin(new_angle) * self.speed
                # 배트 색상 반영: 위쪽 배트의 색상에 해당하는 공 이미지로 교체
                self.image = ball_images[top_bat.color_name]

        # 아래쪽 배트와의 충돌 (공이 아래로 이동 중)
        elif self.dy > 0 and bottom_rect.colliderect(ball_rect):
            if not self.collided:
                self.collided = True
                # 배트 내부에 있을 경우, 배트 바로 위로 위치 조정
                self.y = bottom_rect.top - self.image.get_height() - 1
                offset = random.uniform(-math.pi/16, math.pi/16)
                new_angle = -math.pi/2 + offset  # -90° (즉, 위로)
                self.speed *= 1.05
                self.dx = math.cos(new_angle) * self.speed
                self.dy = math.sin(new_angle) * self.speed
                # 배트 색상 반영: 아래쪽 배트의 색상에 해당하는 공 이미지로 교체
                self.image = ball_images[bottom_bat.color_name]
        else:
            # 충돌 중이 아니면 플래그 초기화
            self.collided = False


# -----------------------------
# 초기 객체 생성
# -----------------------------
# 상단, 하단 배트의 색상을 랜덤(겹치지 않게) 지정
top_color, bottom_color = random.sample(possible_colors, 2)
top_bat = Bat(ctrls=(K_a, K_d), x=450, y=20, width=100, height=10, speed=12, color_key=top_color)
bottom_bat = Bat(ctrls=(K_LEFT, K_RIGHT), x=450, y=570, width=100, height=10, speed=12, color_key=bottom_color)
ball = Ball()

def back_game():
    global ball, game_over, top_bat, bottom_bat, start_time, end_time
    # 새로운 배트 색상(겹치지 않게) 지정하여 객체 재생성
    new_top_color, new_bottom_color = random.sample(possible_colors, 2)
    top_bat = Bat(ctrls=(K_a, K_d), x=450, y=20, width=100, height=10, speed=12, color_key=new_top_color)
    bottom_bat = Bat(ctrls=(K_LEFT, K_RIGHT), x=450, y=570, width=100, height=10, speed=12, color_key=new_bottom_color)
    ball = Ball()
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
        
        # 공이 화면 상단이나 하단을 벗어나면 게임 오버 처리 (자신의 이미지 높이를 사용)
        if ball.y < 0 or ball.y > screen.get_height() - ball.image.get_height():
            game_over = True
            end_time = time.time()

    # 경과 시간 계산 (게임 오버 시 end_time 기준)
    current_time = end_time if game_over else time.time()
    elapsed = int(current_time - start_time)
    minutes = elapsed // 60
    seconds = elapsed % 60
    timer_str = f"Time: {minutes:02}:{seconds:02}"
    # 타이머 텍스트 렌더링 및 투명도 설정
    time_surface = font.render(timer_str, True, (255, 255, 255))
    time_surface.set_alpha(128)
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
