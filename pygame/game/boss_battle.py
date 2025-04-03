import pygame, random, os, pygame.mixer, sys, subprocess
from pygame.locals import *

os.chdir(os.path.dirname(os.path.abspath(__file__)))
main_game_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "main.py")

# 초기화
pygame.init()
pygame.mixer.init()

# 화면 설정
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Boss Battle")

# 색상 정의
WHITE = (255, 255, 255)
RED = (255, 0, 0)
PLAYER_COLOR = WHITE
BOSS_COLORS = [
    (50, 50, 50), (139, 69, 19), (192, 192, 192), (255, 215, 0),
    (135, 206, 250), (0, 128, 0), (0, 0, 255), (128, 0, 128),
    (255, 0, 0), (0, 0, 128)
]
BOSS_RANKS = ["Iron", "Bronze", "Silver", "Gold", "Platinum", "Emerald", "Diamond", "Master", "Grandmaster", "Challenger"]

# 보스 속성
boss_index = 0
boss_health = 5
boss_speed = 5
boss_color = BOSS_COLORS[boss_index]

# 플레이어 속성
player_health = 3
player_speed = 12  # 기존보다 70% 증가
player_hit_timer = 0  # 체력 감소 시 색상 변경 타이머

# 배트 설정
bat_width, bat_height = 10, 100
player_x, player_y = WIDTH - 20, HEIGHT // 2 - bat_height // 2
boss_x, boss_y = 10, HEIGHT // 2 - (bat_height * 3) // 2  # 보스 배트 위치
boss_bat_height = bat_height * 3  # 보스 배트 3배 크기

# 공 설정
ball_img = pygame.image.load("image/ball.png").convert_alpha()
ball_rect = ball_img.get_rect()
balls = []  # 공 리스트

# 보스 공 발사 주기
# 초기 간격: 60프레임, 보스가 늘어날 때마다 5프레임씩 감소, 최소 20프레임 제한
boss_shoot_interval = 60
boss_shoot_timer = 0

# 사운드 로드
hit_sound = pygame.mixer.Sound("sound/hit.wav")
pain_sound = pygame.mixer.Sound("sound/pain.mp3")

# BGM 리스트 설정 (파일 경로를 리스트에 저장)
bgm_tracks = [
    "sound/bgm/bgm1.mp3",
    "sound/bgm/bgm2.mp3",
    "sound/bgm/bgm3.mp3"
]
current_bgm_index = 0

def play_next_bgm():
    global current_bgm_index
    pygame.mixer.music.load(bgm_tracks[current_bgm_index])
    pygame.mixer.music.play()
    pygame.mixer.music.set_endevent(pygame.USEREVENT)

play_next_bgm()

# 게임 오버 화면 함수
def end_screen():
    end_font = pygame.font.Font(None, 80)
    prompt_font = pygame.font.Font(None, 40)
    rank_font = pygame.font.Font(None, 60)
    while True:
        screen.fill((0, 0, 0))
        end_text = end_font.render("Game Over", True, WHITE)
        prompt_text = prompt_font.render("Press Space to exit", True, WHITE)
        # 클리어한 보스 등급과 색상 표시 (boss_color와 BOSS_RANKS[boss_index])
        rank_text = rank_font.render(f"Cleared: {BOSS_RANKS[boss_index]}", True, boss_color)
        screen.blit(end_text, (screen.get_width()//2 - end_text.get_width()//2, screen.get_height()//4))
        screen.blit(rank_text, (screen.get_width()//2 - rank_text.get_width()//2, screen.get_height()//2 - rank_text.get_height()//2))
        screen.blit(prompt_text, (screen.get_width()//2 - prompt_text.get_width()//2, screen.get_height()*3//4))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            subprocess.Popen(["python", main_game_path])
            pygame.quit()
            sys.exit()

# 게임 루프
running = True
clock = pygame.time.Clock()

while running:
    screen.fill((0, 0, 0))
    
    # 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.USEREVENT:
            current_bgm_index = (current_bgm_index + 1) % len(bgm_tracks)
            play_next_bgm()
    
    # 키 입력
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and player_y > 0:
        player_y -= player_speed
    if keys[pygame.K_DOWN] and player_y < HEIGHT - bat_height:
        player_y += player_speed
    
    # 보스 공 발사 (공의 기본 속도 5에 boss_index당 1씩 속도 증가)
    boss_shoot_timer += 1
    if boss_shoot_timer >= boss_shoot_interval:
        boss_shoot_timer = 0
        balls.append([boss_x + bat_width, boss_y + boss_bat_height // 2, 5 + boss_index * 1.0, random.uniform(-4, 4)])
    
    # 공 이동
    for ball in balls:
        ball[0] += ball[2]  # X축 이동
        ball[1] += ball[3]  # Y축 이동
        
        # 화면 위아래 벽에 부딪힐 경우 반사
        if ball[1] <= 0 or ball[1] >= HEIGHT - ball_rect.height:
            ball[3] *= -1
    
    # 플레이어 배트의 Rect (충돌 판정을 실제 배트보다 약간 축소)
    player_rect = pygame.Rect(player_x, player_y, bat_width, bat_height)
    player_rect.inflate_ip(-4, -4)
    
    # 공 충돌 체크
    new_balls = []
    for ball in balls:
        current_ball_rect = ball_img.get_rect(topleft=(ball[0], ball[1]))
        if player_rect.colliderect(current_ball_rect):
            # 플레이어가 공을 받아치면 보스 체력 감소
            boss_health -= 1
            hit_sound.play()
            continue  # 공 제거
        # 만약 공이 오른쪽으로 벗어나면(속도가 빠른 EXPLOSIVE 효과라면) 좌표를 클램핑하여 반사
        elif ball[0] >= WIDTH:
            if ball[2] >= 10:
                ball[0] = WIDTH - ball_rect.width
                ball[2] = -ball[2]
                new_balls.append(ball)
            else:
                player_health -= 1
                player_hit_timer = 18  # 빨간색 효과 타이머
                pain_sound.play()
                continue
        # 만약 공이 왼쪽으로 벗어나면(속도가 빠른 경우) 좌표 클램핑 후 반사
        elif ball[0] <= 0:
            if ball[2] >= 10:
                ball[0] = 0
                ball[2] = -ball[2]
                new_balls.append(ball)
            else:
                boss_health -= 1
                continue
        else:
            new_balls.append(ball)
    balls = new_balls
    
    # 플레이어 체력 체크
    if player_health <= 0:
        end_screen()  # 게임 종료 후 게임 오버 화면으로 전환
    
    # 보스 체력 체크
    if boss_health <= 0:
        if boss_index < len(BOSS_COLORS) - 1:
            boss_index += 1
            boss_color = BOSS_COLORS[boss_index]
            boss_health = 5 + (boss_index * 3)
            boss_shoot_interval = max(20, 60 - boss_index * 5)
        else:
            print("모든 보스를 클리어했습니다!")
            end_screen()
    
    # 플레이어 배트 색상 변경 (체력 감소 시 0.3초 동안 빨간색)
    if player_hit_timer > 0:
        current_player_color = RED
        player_hit_timer -= 1
    else:
        current_player_color = WHITE
    
    # 그래픽 그리기
    pygame.draw.rect(screen, current_player_color, (player_x, player_y, bat_width, bat_height))
    pygame.draw.rect(screen, boss_color, (boss_x, boss_y, bat_width, boss_bat_height))
    
    for ball in balls:
        screen.blit(ball_img, (ball[0], ball[1]))
    
    # 체력 표시 (좌측: 보스 체력, 우측: 플레이어 체력)
    info_font = pygame.font.Font(None, 36)
    boss_text = info_font.render(f"Boss HP: {boss_health}", True, WHITE)
    player_text = info_font.render(f"Player HP: {player_health}/3", True, WHITE)
    screen.blit(boss_text, (20, 20))
    screen.blit(player_text, (WIDTH - 200, 20))
    
    # 보스 등급 텍스트 (등급만 표시) - 화면 상단 중앙에 배치
    rank_text = info_font.render(f"{BOSS_RANKS[boss_index]}", True, boss_color)
    rank_rect = rank_text.get_rect(center=(WIDTH // 2, 20))
    screen.blit(rank_text, rank_rect)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
