import pygame, sys, os, time
from pygame.locals import *

os.chdir(os.path.dirname(os.path.abspath(__file__)))

pygame.init()
pygame.display.set_caption("Pong Game Selection")
screen = pygame.display.set_mode((1000, 600))
clock = pygame.time.Clock()

font = pygame.font.Font(None, 60)
games = ["1vs1"]
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

def game_1vs1():
    import game.pong_game  # pong_game.py가 있어야 합니다.
    game.pong_game.run()

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
                if selected_game == 0:
                    game_1vs1()
            draw_menu()
    clock.tick(30)
