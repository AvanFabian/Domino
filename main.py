from pygame.sprite import Group as Layer
from objects import Domino, Player, Arrow
from pygame.locals import *
import pygame
import random
import sys
import os

#Window configuration
pygame.init()
WIDTH, HEIGHT = 1400, 800
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
GREEN_SCREEN_BKG = ( 0, 187, 45 )

pygame.display.set_caption('Dominó!')

ICON = pygame.image.load("assets/Domino (icon).png").convert()
pygame.display.set_icon(ICON)

PLAYERS_NUM = 4
BACKGROUND = pygame.image.load(f"assets/Table({PLAYERS_NUM}).png").convert()
PLAYER__ = pygame.image.load(f"assets/Dominos (Interface)/jugador#.png").convert()
PLAYER__.set_colorkey( GREEN_SCREEN_BKG )

PLAYER__pos = (26, 606)
PLAYER_NUM_pos = (240, 599)

WINDOW.blit(BACKGROUND, (0, 0))
WINDOW.blit(PLAYER__, PLAYER__pos)

OBJECTS = []#Domino([1, 6], x=200, y=200)]
LAYERS = {0: Layer()}

PLAYERS = [Player() for _ in range(PLAYERS_NUM)]
FPS = 160


class Table:
    def __init__(self):
        self.spacing = 95
        self.dominoes = []
        self.table_dominoes = []

        self.left_iterator = 0
        self.right_iterator = 0
        self.left_positions = []
        self.right_positions = []

        self.left_arrow = Arrow()
        self.right_arrow = Arrow()
        self.left_arrow_orientation = True

    def dominoes_distribution(self):
        for i in range(7):
            for j in range(i, 7):
                self.dominoes.append(Domino((i, j)))

        for player in PLAYERS:
            for _ in range(7):
                player.add_domino(self.draw_random())
    
    def draw_random(self):
        return self.dominoes.pop(random.randint(0, len(self.dominoes)-1))
    
    def draw_by_position(self, position):
        return self.dominoes.pop(position)
    
    def draw_player_number(self, player_number):
        global player_to_play
        player_to_play = pygame.image.load(f"assets/Dominos (Interface)/{player_number + 1}p.png").convert()
        player_to_play.set_colorkey( GREEN_SCREEN_BKG )
        WINDOW.blit(player_to_play, PLAYER_NUM_pos)
        update_layers()

    def draw_player_dominoes(self, player_idx):
        self.erase_player_dominoes()
        spacing = 64

        for domino in PLAYERS[player_idx].dominoes:
            domino.add_position(spacing, 717)
            
            if domino not in OBJECTS:
                OBJECTS.append(domino)

            spacing += 68

    def erase_player_dominoes(self):
        for player_idx in range(0, PLAYERS_NUM):
            for domino in PLAYERS[player_idx].dominoes:
                domino.add_position(9999, 9999)

    def draw_extra_dominoes(self):
        OBJECTS.insert(0, Domino([7, 7], x=548, y=717))

    def is_empty(self):
        return len(self.table_dominoes) == 0
    
    def create_right_positions(self):
        right_x, right_y = 795, 360
        self.right_positions.append([right_x, right_y])
        for _ in range(5):
            right_x, right_y = right_x + self.spacing, right_y
            self.right_positions.append([right_x, right_y])
        
        right_x, right_y = right_x, right_y + self.spacing
        self.right_positions.append([right_x, right_y])
        for _ in range(3):
            right_x, right_y = right_x, right_y + self.spacing
            self.right_positions.append([right_x, right_y])

        right_x, right_y = right_x - self.spacing, right_y
        self.right_positions.append([right_x, right_y])
        for _ in range(5):
            right_x, right_y = right_x - self.spacing, right_y
            self.right_positions.append([right_x, right_y])

        right_x, right_y = right_x, right_y - self.spacing
        self.right_positions.append([right_x, right_y])
        for _ in range(2):
            right_x, right_y = right_x, right_y - self.spacing
            self.right_positions.append([right_x, right_y])

    def create_left_positions(self):
        left_x, left_y = 605,360
        self.left_positions.append([left_x, left_y])
        for _ in range(5):
            left_x, left_y = left_x - self.spacing, left_y
            self.left_positions.append([left_x, left_y])
            
        left_x, left_y = left_x, left_y - self.spacing
        self.left_positions.append([left_x, left_y])
        for _ in range(2):
            left_x, left_y = left_x, left_y - self.spacing
            self.left_positions.append([left_x, left_y])

        left_x, left_y = left_x + self.spacing, left_y
        self.left_positions.append([left_x, left_y])
        for _ in range(9):
            left_x, left_y = left_x + self.spacing, left_y
            self.left_positions.append([left_x, left_y])

        left_x, left_y = left_x, left_y + self.spacing
        self.left_positions.append([left_x, left_y])
        for _ in range(2):
            left_x, left_y = left_x, left_y + self.spacing
            self.left_positions.append([left_x, left_y])
            
        left_x, left_y = left_x - self.spacing, left_y
        self.left_positions.append([left_x, left_y])
        for _ in range(9):
            left_x, left_y = left_x - self.spacing, left_y
            self.left_positions.append([left_x, left_y])

    def can_be_put(self, domino):
        if self.is_empty():
            self.side = "none"
            return True
        
        self.side = ""
        left = self.table_dominoes[0].vals[0]
        right = self.table_dominoes[-1].vals[-1]

        if left in domino.vals: self.side = "left"
        if right in domino.vals: self.side = "right"
        if right in domino.vals and left in domino.vals:
            self.side = "both"

        return left in domino.vals or right in domino.vals
    
    def add_domino_to_table(self, domino):
        if self.side != "both":

            if domino.acotao:
                domino.view_vertical()
            else:
                domino.view_horizontal()

            if self.side == "none":
                self.table_dominoes.insert(0, domino)
                domino.add_position(700, 360)

            if self.side == "left" and domino.vals[1] != self.table_dominoes[0].vals[0] or self.side == "right" and domino.vals[0] != self.table_dominoes[-1].vals[-1]:
                domino.change_orientation_vals()     

            if self.side == "left":
                self.left_placement(domino)

            if self.side == "right":
                self.right_placement(domino)
        
        else:
            self.choose_side(domino)

    def choose_side(self, domino):
        self.activate_arrows()
        choose = True

        while choose:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == MOUSEBUTTONDOWN:
                    if self.right_arrow.click_me():
                        self.side = "right"
                        choose = False
                        break

                    if self.left_arrow.click_me():
                        self.side = "left"
                        choose = False
                        break

            update_layers()

        self.add_domino_to_table(domino)
        self.deactivate_arrows()

    def left_placement(self, domino):
        if self.left_iterator >= 6 and self.left_iterator <= 8:
            domino.change_orientation_sprite()
            domino.view_horizontal()

        elif self.left_iterator >= 8:
            domino.change_orientation_sprite()

        self.table_dominoes.insert(0, domino)
        x, y = self.left_positions[self.left_iterator][0], self.left_positions[self.left_iterator][1]
        domino.add_position(x, y)

        self.left_iterator += 1

    def right_placement(self, domino):
        if self.right_iterator >= 6 and self.right_iterator <= 8:
            domino.change_orientation_sprite()
            domino.view_horizontal()

        elif self.right_iterator >= 8 and self.right_iterator <= 15:
            domino.change_orientation_sprite()

        elif self.right_iterator >= 15 and self.right_iterator <= 17:
            domino.view_horizontal()

        elif self.right_iterator >= 17:
            domino.change_orientation_sprite()

        self.table_dominoes.append(domino)
        x, y = self.right_positions[self.right_iterator][0], self.right_positions[self.right_iterator][1]
        domino.add_position(x, y)

        self.right_iterator += 1

    def players_dominoes(self):
        x, y = 1300, 30
        for player_idx in range(1, PLAYERS_NUM):
            dominoes_amount = len(PLAYERS[player_idx].dominoes)

            if dominoes_amount >= 7:
                dominoes_amount = 7

            num_dominoes = pygame.image.load(f"assets/Dominos (Interface)/{dominoes_amount}.png").convert()
            num_dominoes.set_colorkey( GREEN_SCREEN_BKG )
            WINDOW.blit(num_dominoes, (x, y))
            x, y = x, y + 65

    def activate_arrows(self):
        if self.left_arrow_orientation:
            self.left_arrow.change_orientation_sprite()
            self.left_arrow_orientation = False

        self.right_arrow.add_position(576, 636)
        self.left_arrow.add_position(476, 636)

        if self.left_arrow not in OBJECTS and self.right_arrow not in OBJECTS:
            OBJECTS.insert(1, self.left_arrow)
            OBJECTS.insert(2, self.right_arrow)

        self.right_arrow.update()
        self.left_arrow.update()

    def deactivate_arrows(self):
        self.right_arrow.deactivate()
        self.left_arrow.deactivate()

    def player_plays(self, player_idx):
        played = False

        while played != True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == MOUSEBUTTONDOWN:
                    for domino in PLAYERS[player_idx].dominoes:
                        if domino.click_me():
                            if self.can_be_put(domino):
                                self.add_domino_to_table(domino)
                                PLAYERS[player_idx].dominoes.remove(domino)
                                played = True
                            else:
                                print("!!")
                                    
                    if OBJECTS[0].click_me():
                        try:
                            PLAYERS[player_idx].add_domino(self.draw_random())
                            break
                            #print(PLAYERS[player_idx])

                        except:
                            pass

            self.draw_player_dominoes(player_idx)
            self.players_dominoes()
            update_layers()

        return played

    def computer_plays(self, computer_idx):
        return True

    def start_game(self):
        self.dominoes_distribution()
        self.create_right_positions()
        self.create_left_positions()

        if PLAYERS_NUM < 4:
            self.draw_extra_dominoes()
    
    def __repr__(self):
        return str(self.table_dominoes)


def update_layers():
    WINDOW.blit(BACKGROUND, (0, 0))
    WINDOW.blit(PLAYER__, PLAYER__pos)
    WINDOW.blit(player_to_play, PLAYER_NUM_pos)

    for object in OBJECTS:
        if object.layer not in LAYERS:
            LAYERS[object.layer] = Layer()

        LAYERS[object.layer].add(object)

    for _, layer in LAYERS.items():
        layer.update()
        layer.draw(WINDOW)

    pygame.display.flip()
    pygame.display.update() 


def main():
    table = Table()
    table.start_game()

    clock = pygame.time.Clock()
    TURN = 0  

    while True:
        print(TURN)

        clock.tick(FPS)      
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        if PLAYERS[TURN].manual:
            table.draw_player_number(TURN)
            table.draw_player_dominoes(TURN)
            played = table.player_plays(TURN)

        else:
            played = table.computer_plays(TURN)

        if played:
            played = False
            TURN += 1

            if TURN >= PLAYERS_NUM:
                TURN = 0

        table.players_dominoes()
        update_layers()


if __name__ == '__main__':
    main()