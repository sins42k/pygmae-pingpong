import pygame, random, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 초기화
pygame.init()

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

# 게임 루프
running = True
clock = pygame.time.Clock()

while running:
    screen.fill((0, 0, 0))
    
    # 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 키 입력
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and player_y > 0:
        player_y -= player_speed
    if keys[pygame.K_DOWN] and player_y < HEIGHT - bat_height:
        player_y += player_speed
    
    # 보스 공 발사 (공 속도 증가량을 기존보다 크게 조정)
    boss_shoot_timer += 1
    if boss_shoot_timer >= boss_shoot_interval:
        boss_shoot_timer = 0
        # 공의 기본 속도 5에 boss_index당 1씩 속도 증가
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
    player_rect.inflate_ip(-4, -4)  # 양쪽에서 2픽셀씩 축소하여 판정 범위 감소
    
    # 공 충돌 체크
    new_balls = []
    for ball in balls:
        current_ball_rect = ball_img.get_rect(topleft=(ball[0], ball[1]))
        if player_rect.colliderect(current_ball_rect):
            # 플레이어가 공을 받아치면 보스 체력 감소
            boss_health -= 1
            continue  # 공 제거
        elif ball[0] >= WIDTH:
            # 공이 오른쪽으로 빠져나가면 플레이어 체력 감소
            player_health -= 1
            player_hit_timer = 18  # 0.3초 동안 빨간색 효과
            continue
        elif ball[0] <= 0:
            # 공이 왼쪽으로 빠져나가면 보스 체력 감소
            boss_health -= 1
            continue
        else:
            new_balls.append(ball)
    balls = new_balls
    
    # 플레이어 체력 체크
    if player_health <= 0:
        print("Game Over!")
        running = False
    
    # 보스 체력 체크
    if boss_health <= 0:
        if boss_index < len(BOSS_COLORS) - 1:
            boss_index += 1
            boss_color = BOSS_COLORS[boss_index]
            boss_health = 5 + (boss_index * 3)  # 보스 체력 증가
            # 보스가 늘어날 때마다 발사 간격을 5프레임씩 줄임 (최소 20프레임 제한)
            boss_shoot_interval = max(20, 60 - boss_index * 5)
        else:
            print("모든 보스를 클리어했습니다!")
            running = False
    
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
    font = pygame.font.Font(None, 36)
    boss_text = font.render(f"Boss HP: {boss_health}", True, WHITE)
    player_text = font.render(f"Player HP: {player_health}/3", True, WHITE)
    screen.blit(boss_text, (20, 20))
    screen.blit(player_text, (WIDTH - 200, 20))
    
    # 보스 등급 텍스트 (단어 제거, 등급만 표시) - 화면 상단 중앙에 배치
    rank_text = font.render(f"{BOSS_RANKS[boss_index]}", True, boss_color)
    rank_rect = rank_text.get_rect(center=(WIDTH // 2, 20))
    screen.blit(rank_text, rank_rect)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
