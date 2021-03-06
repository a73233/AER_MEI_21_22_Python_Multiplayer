import pygame
from network import Network
import pickle
import settings
from DTN_OL_client import DTN_OL_client
import threading

pygame.font.init()
width = 700
height = 700
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Client")

magicNumber = settings.magicNumber


class Button:
    def __init__(self, text, x, y, color):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.width = 150
        self.height = 100

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))
        font = pygame.font.SysFont(pygame.font.get_default_font(), 40)
        text = font.render(self.text, 1, (255,255,255))
        win.blit(text, (self.x + round(self.width/2) - round(text.get_width()/2), self.y + round(self.height/2) - round(text.get_height()/2)))

    def click(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        if self.x <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height:
            return True
        else:
            return False


def redrawWindow(win, game, p):
    win.fill((128,128,128))



    if not(game.connected()):
        font = pygame.font.SysFont(pygame.font.get_default_font(), 80)
        text = font.render("Waiting for Player...", 1, (255,0,0), True)
        win.blit(text, (width/2 - text.get_width()/2, height/2 - text.get_height()/2))
    else:
        font = pygame.font.SysFont(pygame.font.get_default_font(), 60)
        text = font.render("Your Move", 1, (0, 255,255))
        win.blit(text, (80, 200))

        text = font.render("Opponents", 1, (0, 255, 255))
        win.blit(text, (380, 200))

        move1 = game.get_player_move(0)
        move2 = game.get_player_move(1)
        if game.bothWent():
            text1 = font.render(move1, 1, (0,0,0))
            text2 = font.render(move2, 1, (0, 0, 0))
        else:
            if game.p1Went and p == 0:
                text1 = font.render(move1, 1, (0,0,0))
            elif game.p1Went:
                text1 = font.render("Locked In", 1, (0, 0, 0))
            else:
                text1 = font.render("Waiting...", 1, (0, 0, 0))

            if game.p2Went and p == 1:
                text2 = font.render(move2, 1, (0,0,0))
            elif game.p2Went:
                text2 = font.render("Locked In", 1, (0, 0, 0))
            else:
                text2 = font.render("Waiting...", 1, (0, 0, 0))

        if p == 1:
            win.blit(text2, (100, 350))
            win.blit(text1, (400, 350))
        else:
            win.blit(text1, (100, 350))
            win.blit(text2, (400, 350))

        for btn in btns:
            btn.draw(win)

    pygame.display.update()


btns = [Button("Rock", 50, 500, (0,0,0)), Button("Scissors", 250, 500, (255,0,0)), Button("Paper", 450, 500, (0,255,0))]

def dc_gui_msg():
    win.fill((128, 128, 128))
    font = pygame.font.SysFont(pygame.font.get_default_font(), 60)
    text = font.render("Waiting for Server Contact", 1, (255,0,0))
    win.blit(text, (100,200))
    pygame.display.update()

def main():
    run = True
    clock = pygame.time.Clock()
    n = Network()

    has_contact = n.tryContactThreaded(timeout=2)
    while(not has_contact):
        dc_gui_msg()
        has_contact = n.tryContactThreaded(timeout=2)

    n.setP(int(n.connect_network()))
    player = n.getP()

    while(player==magicNumber):
        clock.tick(60)
        win.fill((128, 128, 128))
        font = pygame.font.SysFont(pygame.font.get_default_font(), 60)
        text = font.render("Server Full, Try Again.", 1, (255,0,0))
        win.blit(text, (100,200))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                n.setP(int(n.connect_network()))
                player = n.getP()

    print("You are player:", player, " on Address:", n.client.getsockname())
    
    while run:
        has_contact = n.tryContactThreaded(timeout=2)
        while(not has_contact):
            dc_gui_msg()
            has_contact = n.tryContactThreaded(timeout=2)

        clock.tick(60)
        try:
            game = n.send("get")
        except:
            run = False
            print("Couldn't get game")
            break

        if game.bothWent():
            redrawWindow(win, game, player)
            pygame.time.delay(500)
            try:
                game = n.send("reset")
            except:
                run = False
                print("Couldn't get game")
                break

            font = pygame.font.SysFont(pygame.font.get_default_font(), 90)
            if (game.winner() == 1 and player == 1) or (game.winner() == 0 and player == 0):
                text = font.render("You Won!", 1, (255,0,0))
            elif game.winner() == -1:
                text = font.render("Tie Game!", 1, (255,0,0))
            else:
                text = font.render("You Lost...", 1, (255, 0, 0))

            win.blit(text, (width/2 - text.get_width()/2, height/2 - text.get_height()/2))
            pygame.display.update()
            pygame.time.delay(1500)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                n.disconnect_network()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for btn in btns:
                    if btn.click(pos) and game.connected():
                        if player == 0:
                            if not game.p1Went:
                                n.send(btn.text)
                        else:
                            if not game.p2Went:
                                n.send(btn.text)
        try:
            if game.online == False:
                player = int(n.reconnect_network())
                return
            redrawWindow(win, game, player)
        except:
                run = False
                return


def menu_screen():
    run = True
    clock = pygame.time.Clock()

    while run:
        clock.tick(60)
        win.fill((128, 128, 128))
        font = pygame.font.SysFont(pygame.font.get_default_font(), 60)
        text = font.render("Click to Play!", 1, (255,0,0))
        win.blit(text, (100,200))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                run = False
    main()


#DTN_OL_client_instance = DTN_OL_client()
#DTN_OL_client_instance.start()

while True:
    try:
        menu_screen()
    except:
        print("Closed.")
        #DTN_OL_client_instance.cancel()
        break