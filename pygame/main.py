import pygame, sys, os, time
from pygame.locals import *

os.chdir(os.path.dirname(os.path.abspath(__file__)))

pygame.init()
pygame.display.set_caption("Game Selection")
screen = pygame.display.set_mode((1000, 600))
clock = pygame.time.Clock()

font = pygame.font.Font(None, 60)
# 메뉴에 1vs1 Classic과 1vs1 Evolution, 그리고 (필요시) 다른 게임들을 포함합니다.
games = ["1vs1 Classic", "1vs1 Evolution", "Boss Battle", "Gravity"]
selected_game = 0  # 현재 선택된 게임 인덱스

def draw_menu():
    screen.fill((0, 0, 0))
    title = font.render("Select a Game", True, (255, 255, 255))
    screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 50))
    
    for i, game in enumerate(games):
        color = (255, 0, 0) if i == selected_game else (255, 255, 255)
        text = font.render(game, True, color)
        screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, 200 + i * 80))
    
    pygame.display.update()

def countdown():
    for i in range(3, 0, -1):
        screen.fill((0, 0, 0))
        text = font.render(str(i), True, (255, 255, 255))
        screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, screen.get_height() // 2))
        pygame.display.update()
        time.sleep(1)
    
    screen.fill((0, 0, 0))
    text = font.render("GO!", True, (255, 255, 255))
    screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, screen.get_height() // 2))
    pygame.display.update()
    time.sleep(1)

def game_classic():
    # 기존 1vs1 Classic 게임을 실행하는 모듈 호출 (예: game/pong_classic.py)
    import game.pong_classic  
    game.pong_classic.run()

def game_evolution():
    # 새로운 1vs1 Evolution 게임을 실행하는 모듈 호출 (예: game/pong_evolution.py)
    import game.pong_evolution  
    game.pong_evolution.run()

def game_boss():
    # 보스전 게임을 실행하는 모듈 호출 (예: game/boss_battle.py)
    import game.boss_battle  
    game.boss_battle.run()

def game_gravity() :
    # 보스전 게임을 실행하는 모듈 호출 (예: game/gravity.py)
    import game.gravity
    game.gravity.run()

draw_menu()
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_UP:
                selected_game = (selected_game - 1) % len(games)
            elif event.key == K_DOWN:
                selected_game = (selected_game + 1) % len(games)
            elif event.key == K_RETURN:
                countdown()
                # 선택된 게임에 따라 다른 함수를 호출합니다.
                if selected_game == 0:
                    game_classic()
                elif selected_game == 1:
                    game_evolution()
                elif selected_game == 2:
                    game_boss()
                elif selected_game == 3:
                    game_gravity()
            draw_menu()
    clock.tick(30)
