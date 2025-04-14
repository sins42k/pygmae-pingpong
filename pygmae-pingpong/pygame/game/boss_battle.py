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

# 공 이미지 로드 (원본 이미지를 저장)
original_ball_img = pygame.image.load("image/magic.png").convert_alpha()
ball_rect = original_ball_img.get_rect()
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

# 이미지에 tint(톤) 적용 함수
def tint_image(image, tint_color):
    """주어진 이미지에 tint_color의 색상을 적용한 새 이미지를 반환합니다."""
    tinted_image = image.copy()
    tinted_image.fill(tint_color, special_flags=pygame.BLEND_RGBA_MULT)
    return tinted_image

# 게임 오버 화면 함수
def end_screen():
    end_font = pygame.font.Font(None, 80)
    prompt_font = pygame.font.Font(None, 40)
    rank_font = pygame.font.Font(None, 60)
    while True:
        screen.fill((0, 0, 0))
        end_text = end_font.render("Game Over", True, WHITE)
        prompt_text = prompt_font.render("Press Space to exit", True, WHITE)
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
    
    # 키 입력 (플레이어 이동)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and player_y > 0:
        player_y -= player_speed
    if keys[pygame.K_DOWN] and player_y < HEIGHT - bat_height:
        player_y += player_speed
    
    # 보스 공 발사 (공의 기본 속도 5에 boss_index당 1씩 속도 증가)
    boss_shoot_timer += 1
    if boss_shoot_timer >= boss_shoot_interval:
        boss_shoot_timer = 0
        # 보스의 색상을 반영하여 공 이미지에 tint 적용
        tinted_ball_img = tint_image(original_ball_img, boss_color)
        # 공 리스트에 [x, y, x방향 속도, y방향 속도, 해당 공의 이미지] 저장
        balls.append([boss_x + bat_width, boss_y + boss_bat_height // 2, 5 + boss_index * 1.0, random.uniform(-4, 4), tinted_ball_img])
    
    # 공 이동 및 벽 충돌 처리
    new_balls = []
    for ball in balls:
        ball[0] += ball[2]  # X축 이동
        ball[1] += ball[3]  # Y축 이동
        
        # 공 이미지를 이용해 현재 공의 Rect 구하기
        current_ball_rect = ball[4].get_rect(topleft=(ball[0], ball[1]))
        
        # 상단, 하단 벽 충돌시 y 방향 반사
        if ball[1] <= 0 or ball[1] >= HEIGHT - current_ball_rect.height:
            ball[3] *= -1
        
        # 플레이어 배트와 충돌 확인
        player_rect = pygame.Rect(player_x, player_y, bat_width, bat_height)
        player_rect.inflate_ip(-4, -4)
        if player_rect.colliderect(current_ball_rect):
            boss_health -= 1
            hit_sound.play()
            continue  # 공 제거
        
        # 오른쪽 벽(플레이어쪽)에 도달한 경우 : 플레이어 체력 감소, 공 제거
        elif ball[0] >= WIDTH:
            player_health -= 1
            player_hit_timer = 18  # 빨간색 효과 타이머
            pain_sound.play()
            continue
        
        # 왼쪽 벽에 도달하면 기존 로직대로 처리
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
    
    # 플레이어 체력 검사
    if player_health <= 0:
        end_screen()
    
    # 보스 체력 검사 (보스를 클리어하면 다음 보스로 이동)
    if boss_health <= 0:
        if boss_index < len(BOSS_COLORS) - 1:
            boss_index += 1
            boss_color = BOSS_COLORS[boss_index]
            boss_health = 5 + (boss_index * 3)
            boss_shoot_interval = max(20, 60 - boss_index * 5)
        else:
            print("모든 보스를 클리어했습니다!")
            end_screen()
    
    # 플레이어 배트 색상 변경 처리 (피격 시 잠시 빨간색)
    if player_hit_timer > 0:
        current_player_color = RED
        player_hit_timer -= 1
    else:
        current_player_color = WHITE
    
    # 그래픽 그리기
    pygame.draw.rect(screen, current_player_color, (player_x, player_y, bat_width, bat_height))
    pygame.draw.rect(screen, boss_color, (boss_x, boss_y, bat_width, boss_bat_height))
    
    for ball in balls:
        screen.blit(ball[4], (ball[0], ball[1]))
    
    # 체력 및 등급 표시
    info_font = pygame.font.Font(None, 36)
    boss_text = info_font.render(f"Boss HP: {boss_health}", True, WHITE)
    player_text = info_font.render(f"Player HP: {player_health}/3", True, WHITE)
    screen.blit(boss_text, (20, 20))
    screen.blit(player_text, (WIDTH - 200, 20))
    
    rank_text = info_font.render(f"{BOSS_RANKS[boss_index]}", True, boss_color)
    rank_rect = rank_text.get_rect(center=(WIDTH // 2, 20))
    screen.blit(rank_text, rank_rect)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
