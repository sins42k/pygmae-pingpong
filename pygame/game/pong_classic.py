# 셋업
import pygame, sys, os, math, random, time, pygame.mixer, subprocess
from pygame.locals import *

os.chdir(os.path.dirname(os.path.abspath(__file__)))

pygame.init()
pygame.mixer.init()
pygame.display.set_caption("Pong")
screen = pygame.display.set_mode((1000, 600))
clock = pygame.time.Clock()
ball_image = pygame.image.load("image/ball.png").convert_alpha()
main_game_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "main.py")

rscore = 0
lscore = 0

font = pygame.font.Font(None, 40)
font2 = pygame.font.SysFont("corbel", 70)
font3 = pygame.font.Font(None, 60)
font4 = pygame.font.Font(None, 30)

match_start = time.time()

# 사운드 로드
hit_sound = pygame.mixer.Sound("sound/hit.wav")
pain_sound = pygame.mixer.Sound("sound/pain.mp3")

# BGM 리스트 설정 (파일 경로를 리스트에 저장)
bgm_tracks = [
    "sound/bgm/bgm3.mp3",
    "sound/bgm/bgm2.mp3",
    "sound/bgm/bgm1.mp3"
]

current_bgm_index = 0  # 현재 재생 중인 BGM 인덱스

# 배경음악 재생 함수
def play_next_bgm():
    global current_bgm_index
    pygame.mixer.music.load(bgm_tracks[current_bgm_index])  # 현재 인덱스의 BGM 로드
    pygame.mixer.music.play()  # BGM 재생
    pygame.mixer.music.set_endevent(pygame.USEREVENT)  # BGM 끝나면 이벤트 발생

# 최초 BGM 재생
play_next_bgm()

# 클래스 정의
class Bat:
    def __init__(self, ctrls, x, side):
        self.ctrls = ctrls    # 이동 키 목록
        self.x = x            # 배트의 x 좌표
        self.y = 260          # 초기 y 좌표
        self.side = side      # 배트의 방향(-1: 왼쪽, 1: 오른쪽)
        self.lastbop = 0      # 마지막으로 'bop'한 시간 (배트 효과용)
        self.hit_time = 0     # 마지막으로 점수를 잃은(데미지를 입은) 시각

    def move(self):
        # 지정된 키가 눌리면 배트 이동
        if pressed_keys[self.ctrls[0]] and self.y > 0:
            self.y -= 10
        if pressed_keys[self.ctrls[1]] and self.y < 520:
            self.y += 10

    def draw(self):
        # bop 효과를 위한 오프셋 계산 (최근 0.05초 이내 bop 시 약간 이동)
        offset = -self.side * (time.time() < self.lastbop + 0.05) * 10
        # 현재 시간이 hit_time으로부터 0.3초 이내이면 빨간색, 그렇지 않으면 흰색
        color = (255, 0, 0) if time.time() - self.hit_time < 0.3 else (255, 255, 255)
        # 배트를 선으로 그리기
        pygame.draw.line(screen, color, (self.x + offset, self.y),
                         (self.x + offset, self.y + 80), 6)

    def bop(self):
        # bop 효과는 일정 시간 간격 후에만 적용 가능
        if time.time() > self.lastbop + 0.3:
            self.lastbop = time.time()
            
    def hit(self):
        # hit() 호출 시, 점수를 잃은 배트의 hit_time을 현재 시간으로 갱신하여 빨간색 효과를 발생시킴
        self.hit_time = time.time()

class Ball:
    def __init__(self):
        # 공의 초기 방향 및 속도를 무작위로 결정
        self.d = (math.pi/3) * random.random() + (math.pi/3) + math.pi * random.randint(0, 1)
        self.speed = 12
        self.dx = math.sin(self.d) * self.speed
        self.dy = math.cos(self.d) * self.speed
        self.x = 475
        self.y = 275

    def move(self):
        # 공의 위치 업데이트
        self.x += self.dx
        self.y += self.dy

    def draw(self):
        # 공 이미지 그리기
        screen.blit(ball_image, (int(self.x), int(self.y)))

    def bounce(self):
        # 공이 위쪽 또는 아래쪽 경계에 닿으면 y 방향 반사
        if (self.y <= 0 and self.dy < 0) or (self.y >= 550 and self.dy > 0):
            self.dy *= -1
            self.d = math.atan2(self.dx, self.dy)

        # 각 배트와의 충돌 판정
        for bat in bats:
            if pygame.Rect(bat.x, bat.y, 6, 80).colliderect((self.x, self.y), ball_image.get_size()) \
               and abs(self.dx) / self.dx == bat.side:
                # 배트 충돌 시 각도에 약간의 무작위 요소 추가
                self.d += random.random() * math.pi/4 - math.pi/8
                if (0 < self.d < math.pi/6) or (math.pi*5/6 < self.d < math.pi):
                    self.d = ((math.pi/3) * random.random() + (math.pi/3)) + math.pi
                elif (math.pi < self.d < math.pi*7/6) or (math.pi*11/6 < self.d < math.pi*2):
                    self.d = ((math.pi/3) * random.random() + (math.pi/3)) + math.pi    
                self.d *= -1
                self.d %= math.pi * 2

                # bop 효과가 있으면 속도를 증가시킴 (최대 20까지)
                if time.time() < bat.lastbop + 0.05 and self.speed < 30:
                    hit_sound.play()
                    self.speed *= 1.1
                self.dx = math.sin(self.d) * self.speed
                self.dy = math.cos(self.d) * self.speed

# 객체 생성
ball = Ball()
# 왼쪽 배트와 오른쪽 배트를 생성 (각각 컨트롤 키와 방향을 지정)
bats = [Bat([K_w, K_s], 10, -1), Bat([K_UP, K_DOWN], 984, 1)]

# 게임루프
while True:
    clock.tick(30)
    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit()
        if event.type == KEYDOWN:
            # 왼쪽 배트 'bop' 효과 (키 'a' 눌림)
            if event.key == K_a:
                bats[0].bop()
            # 오른쪽 배트 'bop' 효과 (왼쪽 화살표 키 눌림)
            if event.key == K_LEFT:
                bats[1].bop()
        elif event.type == pygame.USEREVENT:  # BGM 종료 이벤트 처리
            current_bgm_index = (current_bgm_index + 1) % len(bgm_tracks)
            play_next_bgm()
    pressed_keys = pygame.key.get_pressed()

    screen.fill((0, 0, 0))
    # 중앙 라인 및 중앙 원 그리기
    pygame.draw.line(screen, (255, 255, 255), (screen.get_width()/2, 0), 
                     (screen.get_width()/2, screen.get_height()), 3)
    pygame.draw.circle(screen, (255, 255, 255), 
                       (int(screen.get_width()/2), int(screen.get_height()/2)), 50, 3)

    # 남은 시간 텍스트 표시
    txt = font.render(str(int(60 - (time.time() - match_start))), True, (255, 255, 255), (0, 0, 0))
    screen.blit(txt, (screen.get_width()/2 - txt.get_width()/2, 20))

    for bat in bats:
        bat.move()
        bat.draw()

    # 공이 왼쪽 경계를 벗어나면 오른쪽 점수 증가 및 왼쪽 배트에 빨간 효과 적용
    if ball.x < -50:
        ball = Ball()
        pain_sound.play()
        rscore += 1
        bats[0].hit()  # 왼쪽 배트에 데미지(hit) 효과 호출
    
    # 공이 오른쪽 경계를 벗어나면 왼쪽 점수 증가 및 오른쪽 배트에 빨간 효과 적용
    if ball.x > 1000:
        ball = Ball()
        pain_sound.play()
        lscore += 1
        bats[1].hit()  # 오른쪽 배트에 데미지(hit) 효과 호출

    ball.move()
    ball.draw()
    ball.bounce()

    # 왼쪽 점수 표시
    txt = font.render(str(lscore), True, (255, 255, 255))
    screen.blit(txt, (20, 20))
    
    # 오른쪽 점수 표시
    txt = font.render(str(rscore), True, (255, 255, 255))
    screen.blit(txt, (980 - txt.get_width(), 20))
    
    # 60초 이후 스코어 화면 및 재시작 로직
    if time.time() - match_start > 60:
        txt = font2.render("score", True, (255, 0, 255))
        screen.blit(txt, (screen.get_width()/4 - txt.get_width()/2, screen.get_height()/4))
        screen.blit(txt, (screen.get_width()*3/4 - txt.get_width()/2, screen.get_height()/4))
        
        txt = font3.render(str(lscore), True, (255, 255, 255))
        screen.blit(txt, (screen.get_width()/4 - txt.get_width()/2, screen.get_height()/2))
        
        txt = font3.render(str(rscore), True, (255, 255, 255))
        screen.blit(txt, (screen.get_width()*3/4 - txt.get_width()/2, screen.get_height()/2))
        
        txt = font4.render("Press Space to restart", True, (255, 255, 255))
        screen.blit(txt, (screen.get_width()*5/9, screen.get_height()-50))

        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit()
            pressed_keys = pygame.key.get_pressed()
            if pressed_keys[K_SPACE]:
                lscore = 0
                rscore = 0
                bats[0].y = 200
                bats[1].y = 200
                match_start = time.time()
                ball = Ball()
                subprocess.Popen(["python", main_game_path])
                pygame.quit()
                sys.exit()
            pygame.display.update()

    pygame.display.update()