import pygame, sys, os, math, random, time, pygame.mixer, subprocess
from pygame.locals import *

os.chdir(os.path.dirname(os.path.abspath(__file__)))

pygame.init()
pygame.mixer.init()
pygame.display.set_caption("1vs1 Evolution")
screen = pygame.display.set_mode((1000, 600))
clock = pygame.time.Clock()
ball_image = pygame.image.load("image/ball.png").convert_alpha()
main_game_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "main.py")

# 점수 초기값
rscore = 0
lscore = 0

font = pygame.font.Font(None, 40)
font2 = pygame.font.Font(None, 70)
font3 = pygame.font.Font(None, 60)
font4 = pygame.font.Font(None, 30)
cooldown_font = pygame.font.Font(None, 20)  # 쿨타임 표시용 폰트

match_start = time.time()
next_skill_grant = match_start + 7  # 7초마다 스킬 지급
last_skill_grant_time = 0  # 마지막 스킬 지급 시각 (그라데이션 효과용)

# 사운드 로드
hit_sound = pygame.mixer.Sound("sound/hit.wav")
pain_sound = pygame.mixer.Sound("sound/pain.mp3")

# BGM 리스트 설정
bgm_tracks = [
    "sound/bgm/bgm3.mp3",
    "sound/bgm/bgm2.mp3",
    "sound/bgm/bgm1.mp3"
]
current_bgm_index = 0

def play_next_bgm():
    global current_bgm_index
    pygame.mixer.music.load(bgm_tracks[current_bgm_index])
    pygame.mixer.music.play()
    pygame.mixer.music.set_endevent(pygame.USEREVENT)

play_next_bgm()

# ── 스킬 상수 (1~9) ──
ICE         = 1   # Ice: 상대방을 얼려 움직임을 멈추게 함; 상징 색상: 파랑
CHANGE      = 2   # Change: 공의 방향을 뒤집고 속도를 증가시킴; 상징 색상: 초록
AURA        = 3   # Aura: 활성화 상태에서 공을 치면 공의 속도를 3배로 강화; 상징 색상: 보라
SHIELD      = 4   # Shield: 상대의 스킬 카운트를 줄임; 상징 색상: 라이트 블루
BOOST       = 5   # Boost: 배트 이동 속도를 3배로 증가시킴; 상징 색상: 빨강
CLONE       = 6   # Clone: 공의 복제체를 생성함; 상징 색상: 골드
TIME        = 7   # Time: 일정 시간 동안 공의 움직임을 정지시킴; 상징 색상: 노랑
SHIFT       = 8   # Shift: 공의 y좌표를 극적으로 변화시킴 (±300); 상징 색상: 마젠타
EXPLOSIVE   = 9   # Explosive: 공의 속도를 2배로 증가시키고 효과를 적용함; 상징 색상: 시안

ALL_SKILLS = [ICE, CHANGE, AURA, SHIELD, BOOST, CLONE, TIME, SHIFT, EXPLOSIVE]

# 전역 SKILL_COLORS 딕셔너리
SKILL_COLORS = {
    ICE: (0, 0, 255),
    CHANGE: (0, 255, 0),
    AURA: (128, 0, 128),
    SHIELD: (135, 206, 235),
    BOOST: (255, 0, 0),
    CLONE: (255, 215, 0),
    TIME: (255, 255, 0),
    SHIFT: (255, 0, 255),
    EXPLOSIVE: (0, 255, 255)
}

# ── 그라데이션 텍스트 렌더 함수 ──
def render_gradient_text(text, font, color_start, color_end):
    surfaces = []
    total_width = 0
    for i, ch in enumerate(text):
        fraction = i / (len(text) - 1) if len(text) > 1 else 0
        r = int(color_start[0] + fraction * (color_end[0] - color_start[0]))
        g = int(color_start[1] + fraction * (color_end[1] - color_start[1]))
        b = int(color_start[2] + fraction * (color_end[2] - color_start[2]))
        letter_surface = font.render(ch, True, (r, g, b))
        surfaces.append(letter_surface)
        total_width += letter_surface.get_width()
    result = pygame.Surface((total_width, max(s.get_height() for s in surfaces)), pygame.SRCALPHA)
    x_offset = 0
    for s in surfaces:
        result.blit(s, (x_offset, 0))
        x_offset += s.get_width()
    return result

# ── SkillCard 클래스 ──
class SkillCard:
    def __init__(self, ability, ability_count, last_used, is_right=False):
        self.ability = ability
        self.ability_count = ability_count
        self.last_used = last_used  # 스킬 마지막 사용 시간
        self.is_right = is_right
        self.colors = SKILL_COLORS
        self.width = 40
        self.height = 40
        self.font = pygame.font.Font(None, 30)
    
    def draw(self, x, y):
        # 스킬 카드 그리기
        card_color = self.colors.get(self.ability, (255, 255, 255))
        pygame.draw.rect(screen, card_color, (x, y, self.width, self.height))
        pygame.draw.rect(screen, (0, 0, 0), (x, y, self.width, self.height), 2)
        text = self.font.render(str(self.ability_count), True, (0, 0, 0))
        screen.blit(text, (x + self.width/2 - text.get_width()/2, y + self.height/2 - text.get_height()/2))
        # 쿨타임 계산 (스킬 사용 후 3초 쿨타임)
        remaining = max(0, self.last_used + 3 - time.time())
        cd_text = cooldown_font.render(f"{remaining:.1f}", True, (128, 128, 128))
        # 오른쪽 플레이어일 경우 카드 왼쪽에, 아니면 카드 오른쪽에 표시
        if self.is_right:
            screen.blit(cd_text, (x - cd_text.get_width() - 5, y + self.height/2 - cd_text.get_height()/2))
        else:
            screen.blit(cd_text, (x + self.width + 5, y + self.height/2 - cd_text.get_height()/2))

# ── FakeBall 클래스 ──
class FakeBall:
    def __init__(self, real_ball):
        self.x = real_ball.x
        self.y = real_ball.y
        self.d = real_ball.d + random.uniform(-0.3, 0.3)
        self.speed = real_ball.speed
        self.dx = math.sin(self.d) * self.speed
        self.dy = math.cos(self.d) * self.speed
        self.creation_time = time.time()
        self.lifetime = 1.5

    def move(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self):
        image = ball_image.copy()
        screen.blit(image, (int(self.x), int(self.y)))

fake_balls = []

# ── Bat 클래스 ──
class Bat:
    def __init__(self, ctrls, x, side):
        self.ctrls = ctrls
        self.x = x
        self.y = 260
        self.side = side
        self.lastbop = 0
        self.hit_time = 0
        self.last_ability_used = 0
        self.speed_boost_end = 0
        self.speed = 10

        self.freeze_active = False
        self.freeze_end = 0
        self.frozen_by = None
        self.aura_active = False
        self.aura_end = 0

        self.ability = random.choice(ALL_SKILLS)
        self.ability_count = 1
    
    def move(self):
        if self.freeze_active and time.time() < self.freeze_end:
            return
        current_speed = self.speed * 3 if time.time() < self.speed_boost_end else self.speed
        if pressed_keys[self.ctrls[0]] and self.y > 0:
            self.y -= current_speed
        if pressed_keys[self.ctrls[1]] and self.y < 520:
            self.y += current_speed

    def draw(self):
        draw_x = self.x
        if self.freeze_active and time.time() < self.freeze_end and self.frozen_by == ICE:
            color = SKILL_COLORS[ICE]
        elif time.time() < self.speed_boost_end:
            color = SKILL_COLORS[BOOST]
        elif time.time() - self.hit_time < 0.3:
            color = SKILL_COLORS[CHANGE]
        else:
            color = (255, 255, 255)
        pygame.draw.line(screen, color, (draw_x, self.y), (draw_x, self.y + 80), 6)
        if self.aura_active and time.time() < self.aura_end:
            bat_rect = pygame.Rect(draw_x, self.y, 6, 80)
            aura_rect = bat_rect.inflate(20, 20)
            pygame.draw.ellipse(screen, SKILL_COLORS[AURA], aura_rect, 4)

    def bop(self):
        if time.time() > self.lastbop + 0.3:
            self.lastbop = time.time()
            
    def hit(self):
        self.hit_time = time.time()
        
    def use_ability(self, opponent, ball):
        # 쿨타임 3초 적용
        if self.ability_count <= 0 or self.ability is None or time.time() < self.last_ability_used + 3:
            return
        self.last_ability_used = time.time()
        
        if self.ability == ICE:
            opponent.freeze_active = True
            opponent.freeze_end = time.time() + 1.5
            opponent.frozen_by = ICE
        elif self.ability == CHANGE:
            ball.d = (ball.d + math.pi) % (2 * math.pi)
            ball.speed *= 1.5
            ball.dx = math.sin(ball.d) * ball.speed
            ball.dy = math.cos(ball.d) * ball.speed
            ball.flash = time.time() + 0.3
            ball.flash_color = SKILL_COLORS[CHANGE]
        elif self.ability == AURA:
            self.aura_active = True
            self.aura_end = time.time() + 2
        elif self.ability == SHIELD:
            if opponent.ability_count > 0:
                opponent.ability_count = max(0, opponent.ability_count - 3)
                if opponent.ability_count == 0:
                    opponent.ability = None
        elif self.ability == BOOST:
            self.speed_boost_end = time.time() + 2
        elif self.ability == CLONE:
            fake_balls.append(FakeBall(ball))
            fake_balls.append(FakeBall(ball))
        elif self.ability == TIME:
            ball.freeze_end = time.time() + 2
            ball.freeze_color = SKILL_COLORS[TIME]
        elif self.ability == SHIFT:
            ball.y += random.uniform(-300, 300)
        elif self.ability == EXPLOSIVE:
            ball.speed *= 2
            ball.dx = math.sin(ball.d) * ball.speed
            ball.dy = math.cos(ball.d) * ball.speed
            ball.flash = time.time() + 0.3
            ball.flash_color = SKILL_COLORS[EXPLOSIVE]
            # 공이 맵 밖으로 사라지지 않도록 좌표 클램핑
            ball.x = max(0, min(ball.x, screen.get_width() - ball_image.get_width()))
            ball.y = max(0, min(ball.y, screen.get_height() - ball_image.get_height()))
        
        self.ability_count -= 1
        self.ability = random.choice(ALL_SKILLS)

# ── Ball 클래스 ──
class Ball:
    def __init__(self):
        self.d = (math.pi / 3) * random.random() + (math.pi / 3) + math.pi * random.randint(0, 1)
        self.speed = 12
        self.base_speed = self.speed
        self.dx = math.sin(self.d) * self.speed
        self.dy = math.cos(self.d) * self.speed
        self.x = 475
        self.y = 275
        self.flash = 0
        self.flash_color = (0, 255, 0)
        self.freeze_end = 0

    def move(self):
        if time.time() < self.freeze_end:
            return
        self.x += self.dx
        self.y += self.dy
        if time.time() > self.flash:
            self.speed = self.base_speed
            self.dx = math.sin(self.d) * self.speed
            self.dy = math.cos(self.d) * self.speed

    def draw(self):
        screen.blit(ball_image, (int(self.x), int(self.y)))
        if time.time() < self.flash:
            pygame.draw.circle(screen, self.flash_color,
                               (int(self.x + ball_image.get_width()/2), int(self.y + ball_image.get_height()/2)),
                               int(ball_image.get_width()/2) + 10, 3)
        if time.time() < self.freeze_end:
            overlay = pygame.Surface((ball_image.get_width(), ball_image.get_height()))
            overlay.set_alpha(128)
            overlay.fill(SKILL_COLORS[TIME])
            screen.blit(overlay, (int(self.x), int(self.y)))

    def bounce(self):
        ball_rect = pygame.Rect(int(self.x), int(self.y), ball_image.get_width(), ball_image.get_height())
        if (self.y <= 0 and self.dy < 0) or (self.y + ball_image.get_height() >= 600 and self.dy > 0):
            self.dy *= -1
            self.d = math.atan2(self.dx, self.dy)
        for bat in bats:
            bat_rect = pygame.Rect(bat.x, bat.y, 6, 80)
            if bat_rect.colliderect(ball_rect):
                self.speed *= 1.05
                self.d += random.random() * math.pi/4 - math.pi/8
                if (0 < self.d < math.pi/6) or (math.pi * 5/6 < self.d < math.pi):
                    self.d = ((math.pi/3) * random.random() + (math.pi/3)) + math.pi
                elif (math.pi < self.d < math.pi*7/6) or (math.pi*11/6 < self.d < math.pi*2):
                    self.d = ((math.pi/3) * random.random() + (math.pi/3)) + math.pi    
                self.d *= -1
                self.d %= math.pi * 2
                for bat_candidate in bats:
                    if bat_candidate.aura_active and time.time() < bat_candidate.aura_end:
                        self.speed *= 3
                        break
                if time.time() < bat.lastbop + 0.05 and self.speed < 20:
                    self.speed *= 1.1
                self.dx = math.sin(self.d) * self.speed
                self.dy = math.cos(self.d) * self.speed
                if self.dx > 0:
                    self.x = bat_rect.right
                else:
                    self.x = bat_rect.left - ball_image.get_width()
                break

# ── 게임 종료 후 다른 페이지(게임 오버) 화면 함수 ──
def end_screen():
    end_font = pygame.font.Font(None, 80)
    prompt_font = pygame.font.Font(None, 40)
    while True:
        screen.fill((0, 0, 0))
        end_text = end_font.render("Game Over", True, (255, 255, 255))
        prompt_text = prompt_font.render("Press Space to exit", True, (255, 255, 255))
        screen.blit(end_text, (screen.get_width()/2 - end_text.get_width()/2, screen.get_height()/3))
        screen.blit(prompt_text, (screen.get_width()/2 - prompt_text.get_width()/2, screen.get_height()*2/3))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_SPACE]:
            subprocess.Popen(["python", main_game_path])
            pygame.quit()
            sys.exit()

# ── 객체 생성 ──
ball = Ball()
bats = [Bat([pygame.K_w, pygame.K_s], 10, -1), Bat([pygame.K_UP, pygame.K_DOWN], 984, 1)]

# ── 게임루프 ──
while True:
    clock.tick(30)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                bats[0].bop()
            if event.key == pygame.K_RSHIFT:
                bats[1].bop()
            if event.key == pygame.K_d:
                bats[0].use_ability(bats[1], ball)
            if event.key == pygame.K_LEFT:
                bats[1].use_ability(bats[0], ball)
        elif event.type == pygame.USEREVENT:
            current_bgm_index = (current_bgm_index + 1) % len(bgm_tracks)
            play_next_bgm()
    pressed_keys = pygame.key.get_pressed()

    screen.fill((0, 0, 0))
    # 중앙 선을 하얀색으로 그리기
    pygame.draw.line(screen, (255, 255, 255), (screen.get_width()/2, 0),
                     (screen.get_width()/2, screen.get_height()), 3)
    pygame.draw.circle(screen, SKILL_COLORS[AURA], (int(screen.get_width()/2), int(screen.get_height()/2)), 50, 3)

    # 경기 시간 남은 초를 표시 (스킬 지급 직후 0.5초 동안 그라데이션 효과 적용)
    remaining_time = int(120 - (time.time() - match_start))
    time_str = str(remaining_time)
    if last_skill_grant_time and time.time() - last_skill_grant_time < 0.5:
        # 그라데이션: 황금색 -> 로열블루
        clock_surface = render_gradient_text(time_str, font, (255,215,0), (65,105,225))
    else:
        clock_surface = font.render(time_str, True, (255,255,255), (0,0,0))
    screen.blit(clock_surface, (screen.get_width()/2 - clock_surface.get_width()/2, 20))

    if time.time() >= next_skill_grant:
        # 스킬 지급 시각 갱신
        last_skill_grant_time = time.time()
        for bat in bats:
            if bat.ability is None:
                bat.ability = random.choice(ALL_SKILLS)
                bat.ability_count = 1
            else:
                bat.ability_count += 1
        next_skill_grant += 7

    for bat in bats:
        bat.move()
        bat.draw()

    if ball.x < -50:
        ball = Ball()
        pain_sound.play()
        rscore += 1
        bats[0].hit()
        if bats[0].ability is None:
            bats[0].ability = random.choice(ALL_SKILLS)
            bats[0].ability_count = 2
        else:
            bats[0].ability_count += 2

    if ball.x > 1000:
        ball = Ball()
        pain_sound.play()
        lscore += 1
        bats[1].hit()
        if bats[1].ability is None:
            bats[1].ability = random.choice(ALL_SKILLS)
            bats[1].ability_count = 2
        else:
            bats[1].ability_count += 2

    ball.move()
    ball.draw()
    ball.bounce()

    for fb in fake_balls[:]:
        if time.time() - fb.creation_time > fb.lifetime:
            fake_balls.remove(fb)
        else:
            fb.move()
            fb.draw()

    txt = font.render(str(lscore), True, (255,255,255))
    screen.blit(txt, (20, 20))
    
    txt = font.render(str(rscore), True, (255,255,255))
    screen.blit(txt, (980 - txt.get_width(), 20))
    
    left_card = SkillCard(bats[0].ability, bats[0].ability_count, bats[0].last_ability_used, is_right=False)
    right_card = SkillCard(bats[1].ability, bats[1].ability_count, bats[1].last_ability_used, is_right=True)
    left_card.draw(20, 60)
    right_card.draw(980 - 40, 60)
    
    if time.time() - match_start > 120:
        # 게임 종료 후, 스페이스바를 누르면 다른 페이지(게임 오버)로 넘어감
        end_screen()

    pygame.display.update()
