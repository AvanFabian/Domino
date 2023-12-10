# pyinstaller main.py --onefile --noconsole --add-data "assets;assets" --add-data "venv;venv"
from assets.originalobjects import Domino, Player, Button
from pygame.sprite import Group as Layer
from pygame.locals import *
import numpy as np
# import asyncio
import random
import pygame
import time
import sys


#Window configuration
pygame.init()
WIDTH, HEIGHT = 1400, 800
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption('Dominó!')

ICON = pygame.image.load("assets/DominoIcon.png").convert_alpha()
pygame.display.set_icon(ICON)

PLAYERS_NUM = 2
last_players_num = PLAYERS_NUM

BACKGROUND = pygame.image.load(f"assets/Table({PLAYERS_NUM}).png").convert_alpha()
PLAYER__ = pygame.image.load(f"assets/Dominos (Interface)/jugador#.png").convert_alpha()

SLEEP_TIME = .16
PLAYER__pos = (26, 606)
PLAYER_NUM_pos = (240, 599)
can_play_pos = (310, 614)
turn_pos = (625, 6)

WINDOW.blit(BACKGROUND, (0, 0))
WINDOW.blit(PLAYER__, PLAYER__pos)

OBJECTS = []
LAYERS = {0: Layer()}

PLAYERS = [Player(num) for num in range(PLAYERS_NUM)]

#Player
player = PLAYERS[0]

#computer
#PLAYERS[0].change_auto()
PLAYERS[1].change_auto()
#PLAYERS[2].change_auto()
#PLAYERS[3].change_auto()

FPS = 30


text_color = (59, 32, 39)
bck_color = (255, 194, 161)

X = WIDTH
Y = HEIGHT

font = pygame.font.Font('assets/alagard.ttf', 32)

GAME_FINISHED_SOUND =  pygame.mixer.Sound('assets/Audio/gameFinished.wav')
EXTRA_DOMINO_SOUND =  pygame.mixer.Sound('assets/Audio/newDomino.wav')
BUTTOM_SOUND =  pygame.mixer.Sound('assets/Audio/Buttom.wav')


class Table():
    def __init__(self):
        self.turn = 0
        self.spacing = 95
        self.first_game = True
        self.dominoes = np.array([], dtype=object)
        self.table_dominoes = np.array([], dtype=object)

        self.left_iterator = 0
        self.right_iterator = 0
        self.left_positions = []
        self.right_positions = []

        self.last_player = None
        self.extra_domino = False
        self.extra_dominoes = None
        self.left_arrow_orientation = True
        self.left_arrow = Button("arrow1.png")
        self.right_arrow = Button("arrow1.png")

        self.extra_domino = False
        self.extra_x, self.extra_y = 0, 0

        self.capicua_bool = False

    def dominoes_distribution(self):
        for i in range(7):
            for j in range(i, 7):
                self.dominoes = np.append(self.dominoes, Domino((i, j)))

        for player in PLAYERS:
            for _ in range(7):
                player.add_domino(self.draw_random())
    
    def draw_random(self):
        domino = np.random.choice(self.dominoes)
        self.dominoes = np.delete(self.dominoes, np.where(self.dominoes == domino))
        return domino
    
    def extra_domino_sprite(self):
        extra_domino = pygame.image.load(f"assets/Dominos (Interface)/+.png").convert_alpha()
        WINDOW.blit(extra_domino, (self.extra_x, self.extra_y))

    def draw_player_number(self, player_number):
        global player_to_play
        player_to_play = pygame.image.load(f"assets/Dominos (Interface)/{player_number + 1}p.png").convert_alpha()
        WINDOW.blit(player_to_play, PLAYER_NUM_pos)
        update_layers()

    def draw_player_dominoes(self, player_idx):
        if PLAYERS[player_idx].manual:
            x_padding = 68
            y_padding = 160

            x, y = 64, 717
            aux = 1

            for domino in PLAYERS[player_idx].dominoes:
                if domino not in OBJECTS:
                    OBJECTS.append(domino)

                domino.add_position(x, y)
                domino.show()

                if aux == 7:
                    x, y = 64, 717
                    y -= y_padding
                    aux = 0

                    y_padding += 100
                
                else:
                    x += x_padding
                    pass

                aux += 1 

    def erase_player_dominoes(self, player_idx):
        players = [index for index, player in enumerate(PLAYERS) if index != player_idx]

        for player in players:
            if PLAYERS[player].manual:
                for domino in PLAYERS[player].dominoes:
                    domino.hide()

    def draw_extra_dominoes(self):
        self.extra_dominoes = Domino([7, 7], x=548, y=717)
        OBJECTS.insert(0, self.extra_dominoes)

    def hide_extra_dominoes(self):
        self.extra_dominoes.extra_dominoes_is_empty()
        self.extra_dominoes.hide()

    def is_empty(self):
        return len(self.table_dominoes) == 0
    
    def create_right_positions(self):
        right_x, right_y = 795, 360

        self.right_positions.append([right_x, right_y])
        for _ in range(5):
            right_x += self.spacing
            self.right_positions.append([right_x, right_y])
        
        for _ in range(4):
            right_y += self.spacing
            self.right_positions.append([right_x, right_y])

        for _ in range(6):
            right_x -= self.spacing
            self.right_positions.append([right_x, right_y])

        for _ in range(2):
            right_y -= self.spacing
            self.right_positions.append([right_x, right_y])

        for _ in range(6):
            right_x -= self.spacing
            self.right_positions.append([right_x, right_y])

        right_y -= self.spacing
        self.right_positions.append([right_x, right_y])

        for _ in range(5):
            right_x += self.spacing
            self.right_positions.append([right_x, right_y])

        self.right_positions = np.array(self.right_positions)

    def create_left_positions(self):
        left_x, left_y = 605,360

        self.left_positions.append([left_x, left_y])
        for _ in range(5):
            left_x -= self.spacing
            self.left_positions.append([left_x, left_y])
            
        for _ in range(3):
            left_y -= self.spacing
            self.left_positions.append([left_x, left_y])

        for _ in range(10):
            left_x += self.spacing
            self.left_positions.append([left_x, left_y])

        for _ in range(2):
            left_y += self.spacing
            self.left_positions.append([left_x, left_y])
            
        for _ in range(8):
            left_x -= self.spacing
            self.left_positions.append([left_x, left_y])

        self.left_positions = np.array(self.left_positions)

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
    
    def add_domino_to_table(self, domino, side=None):
        if side is not None:
            self.side = side

        if self.side != "both":
            if domino.acotao:
                domino.view_vertical()
            else:
                domino.view_horizontal()

            if self.side == "none":
                self.table_dominoes = np.insert(self.table_dominoes, 0, domino)
                domino.change_orientation_sprite()
                domino.add_position(700, 360)

            if self.side == "left" and domino.vals[1] != self.table_dominoes[0].vals[0] or self.side == "right" and domino.vals[0] != self.table_dominoes[-1].vals[-1]:
                domino.change_orientation_vals()     

            if self.side == "left":
                self.left_placement(domino)

            if self.side == "right":
                self.right_placement(domino)

            domino.domino_placed()
            domino_sound()
        
        else:
            self.choose_side(domino)

    def choose_side(self, domino):
        self.activate_arrows()
        update_layers()
        choose = True

        while choose:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == MOUSEBUTTONDOWN:
                    if self.right_arrow.click_me():
                        #BUTTOM_SOUND.play()
                        self.side = "right"
                        choose = False
                        break

                    if self.left_arrow.click_me():
                        #BUTTOM_SOUND.play()
                        self.side = "left"
                        choose = False
                        break

            update_layers()

        self.add_domino_to_table(domino)
        self.deactivate_arrows()

    def left_placement(self, domino):
        domino.change_orientation_sprite()
        if self.left_iterator >= 6 and self.left_iterator <= 8:
            domino.change_orientation_sprite()
            domino.view_horizontal()

        elif self.left_iterator >= 8 and self.left_iterator <= 18:
            domino.change_orientation_sprite()

        elif self.left_iterator >= 18 and self.left_iterator <= 19:
            domino.view_horizontal()
        
        elif self.left_iterator >= 19:
            domino.view_vertical()
            
        self.table_dominoes = np.insert(self.table_dominoes, 0, domino)
        print(f"self.left_iterator: {self.left_iterator}")
        print(f"self.left_positions[self.left_iterator]: {self.left_positions[self.left_iterator]}")
        x, y = self.left_positions[self.left_iterator][0], self.left_positions[self.left_iterator][1]
        domino.add_position(x, y)

        self.left_iterator += 1

    def right_placement(self, domino):
        domino.change_orientation_sprite()
        if self.right_iterator >= 6 and self.right_iterator <= 9:
            domino.change_orientation_sprite()
            domino.view_horizontal()

        elif self.right_iterator >= 9 and self.right_iterator <= 15:
            domino.change_orientation_sprite()

        elif self.right_iterator >= 15 and self.right_iterator <= 17:
            domino.view_horizontal()

        elif self.right_iterator >= 17 and self.right_iterator <= 23:
            domino.change_orientation_sprite()
        
        elif self.right_iterator >= 23 and self.right_iterator <= 24:
            domino.view_horizontal()

        elif self.right_iterator >= 24:
            domino.view_vertical()

        self.table_dominoes = np.append(self.table_dominoes, domino)
        print(f"self.right_iterator: {self.right_iterator}")
        print(f"self.right_positions[self.right_iterator]: {self.right_positions[self.right_iterator]}")
        x, y = self.right_positions[self.right_iterator][0], self.right_positions[self.right_iterator][1]
        domino.add_position(x, y)

        self.right_iterator += 1

    def players_dominoes(self):
        x, y = 1290, 30
        num_x, num_y = 1240, 12
        turn_x, turn_y = 1160, 25
        sprite_added = True

        for player in PLAYERS:
            dominoes_amount = len(player.dominoes)

            if dominoes_amount >= 7:
                dominoes_amount = 7

            num_dominoes = pygame.image.load(f"assets/Dominos (Interface)/{dominoes_amount}.png").convert_alpha()
            player_num = pygame.image.load(f"assets/Dominos (Interface)/{player.num + 1}p.png").convert_alpha()

            if self.turn == player.num:
                player_turn = pygame.image.load(f"assets/Dominos (Interface)/turn.png").convert_alpha()
                self.extra_x, self.extra_y = turn_x - 46, turn_y - 6
                
                if self.extra_domino and sprite_added:
                    self.extra_domino_sprite()
                    sprite_added = False

            else:
                player_turn = pygame.image.load(f"assets/Dominos (Interface)/0.png").convert_alpha()

            WINDOW.blit(player_turn, (turn_x, turn_y))
            WINDOW.blit(num_dominoes, (x, y))
            WINDOW.blit(player_num, (num_x, num_y))

            y += 65
            num_y += 64
            turn_y += 64

    def activate_arrows(self):
        if self.left_arrow_orientation:
            self.left_arrow.change_orientation_sprite()
            self.left_arrow_orientation = False

        self.right_arrow.add_position(576, 636)
        self.left_arrow.add_position(476, 636)
        self.right_arrow.activate()
        self.left_arrow.activate()

        if self.left_arrow not in OBJECTS and self.right_arrow not in OBJECTS:
            OBJECTS.insert(1, self.left_arrow)
            OBJECTS.insert(2, self.right_arrow)
            self.left_arrow.arrow = True
            self.right_arrow.arrow = True

    def deactivate_arrows(self):
        self.right_arrow.deactivate()
        self.left_arrow.deactivate()

    def create_buttons(self):
        global PASS
        global REPEAT
        global FULLSCREEN
        global EXIT

        PASS = Button("PASS_button1.png")
        REPEAT = Button("REPEAT_button1.png")
        FULLSCREEN = Button("FULLSCREEN_button1.png")
        EXIT = Button("EXIT_button1.png")

        x, y = 598, 678
        buttons = [PASS, REPEAT, FULLSCREEN, EXIT]

        for button in buttons:
            button.add_position(x, y)
            y += 26

        for button in buttons:
            button.activate()
            if button not in OBJECTS:
                OBJECTS.append(button)

    def draw_player_interface(self, player):
        self.draw_player_dominoes(player.num)
        self.draw_player_number(player.num)
        update_layers()

    def player_plays(self, player_idx):
        self.erase_player_dominoes(player_idx)
        self.draw_player_dominoes(player_idx)
        
        global PLAYERS_NUM
        global can_play

        can_play = None
        played = False

        while played != True:
            if len(self.dominoes) == 0 and self.extra_dominoes is not None:
                self.hide_extra_dominoes()

            aux = gameManager.check_player_dominoes(PLAYERS[TURN])
            if aux:
                can_play = pygame.image.load(f"assets/Dominos (Interface)/0.png").convert_alpha()

            else:
                can_play = pygame.image.load(f"assets/Dominos (Interface)/no vas.png").convert_alpha()
                if len(self.table_dominoes) < PLAYERS_NUM and len(self.dominoes) == 0:
                    if PLAYERS_NUM == 2:
                        try: PLAYERS[player_idx - 1].add_points(30)
                        except: PLAYERS[-1].add_points(30)

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == MOUSEBUTTONDOWN:
                    for domino in PLAYERS[player_idx].dominoes:
                        if domino.click_me():
                            if self.can_be_put(domino):
                                self.add_domino_to_table(domino)
                                PLAYERS[player_idx].dominoes = np.delete(PLAYERS[player_idx].dominoes, np.where(PLAYERS[player_idx].dominoes == domino))
                                self.draw_player_dominoes(player_idx)
                                played = True

                    if self.extra_dominoes is not None:
                        if self.extra_dominoes.click_me():
                            EXTRA_DOMINO_SOUND.play()

                            PLAYERS[player_idx].add_domino(self.draw_random())
                            self.draw_player_dominoes(player_idx)

                            if len(self.table_dominoes) < PLAYERS_NUM and PLAYERS[player_idx].first_pick:
                                print("Son 30!!")
                                
                                try: PLAYERS[player_idx - 1].add_points(30)
                                except: PLAYERS[-1].add_points(30)

                                PLAYERS[player_idx].first_pick = False

                            self.extra_domino = True

                    if PASS.click_me():
                        BUTTOM_SOUND.play()
                        played = True

                    if REPEAT.click_me():
                        BUTTOM_SOUND.play()
                        PLAYERS_NUM = 2
                        played = -1
                        return played

                    if FULLSCREEN.click_me():
                        BUTTOM_SOUND.play()
                        PLAYERS_NUM = 3
                        played = -1
                        return played

                    if EXIT.click_me():
                        BUTTOM_SOUND.play()
                        PLAYERS_NUM = 4
                        played = -1
                        return played

            update_layers()

        can_play = pygame.image.load(f"assets/Dominos (Interface)/0.png").convert_alpha()
        time.sleep(SLEEP_TIME)
        return played

    def capicua(self):
        if self.table_dominoes[0].vals[0] == self.table_dominoes[-1].vals[-1]:
            self.capicua_bool = True
            return True
        else:
            self.capicua_bool = False
            return False

    def repeat_game(self):
        OBJECTS = []
        LAYERS = {0: Layer()}

        for player in PLAYERS:
            player.remove_all()

        self.dominoes = np.array([])
        self.table_dominoes = np.array([])
        self.left_iterator = 0
        self.right_iterator = 0

        return OBJECTS, LAYERS

    def start_game(self):
        self.capicua_bool = False
        self.dominoes_distribution()
        self.create_buttons()

        if self.first_game:
            #self.draw_player_interface(player)
            self.create_right_positions()
            self.create_left_positions()
            self.first_game = False

        if PLAYERS_NUM < 4:
            self.draw_extra_dominoes()

    def return_state(self):
        return self.table_dominoes

    def __repr__(self):
        return str(self.table_dominoes)


class Fake_Table():
    def __init__(self, state=None):
        if state is not None: 
            self.fake_table = state

        else: 
            self.fake_table = np.array([], dtype=object)
        
    def childrens(self, computer_idx):
        playable_dominoes = self.check_computer_dominoes(computer_idx)
        childrens = []

        for domino, side in playable_dominoes:
            child_state = list(self.fake_table.copy())
            child = self.add_domino_to_fake_table(child_state, domino, side)
            childrens.append(Fake_Table(state=child))

        return childrens
    
    def check_computer_dominoes(self, computer_idx):
        playable_dominoes = []
        for domino in PLAYERS[computer_idx].dominoes:
            if self.is_empty():
                playable_dominoes.append([domino, "none"])
                continue
        
            left = self.fake_table[0].vals[0]
            right = self.fake_table[-1].vals[-1]

            if left in domino.vals and right not in domino.vals:
                playable_dominoes.append([domino, "left"])

            if right in domino.vals and left not in domino.vals:
                playable_dominoes.append([domino, "right"])

            if right in domino.vals and left in domino.vals:
                domino_copy = domino.__copy__()
                playable_dominoes.append([domino, "right"])
                playable_dominoes.append([domino_copy, "left"])

        return playable_dominoes
    
    def add_domino_to_fake_table(self, fake_table, domino, side):
        if side == "left" and domino.vals[1] != fake_table[0].vals[0]:
            domino.change_orientation_vals()
            fake_table.insert(0, domino)

        elif side == "left":
            fake_table.insert(0, domino)

        if side == "right" and domino.vals[0] != fake_table[-1].vals[-1]:
            domino.change_orientation_vals()
            fake_table.append(domino)

        elif side == "right":
            fake_table.append(domino)

        if side == "none":
            fake_table.append(domino)
        
        return fake_table
    
    def heuristic(self, computer_idx):
        computer = PLAYERS[computer_idx]
        heuristic = 0

        playable_dominoes = self.check_computer_dominoes(computer_idx)
        if len(playable_dominoes) >= 1:
            heuristic += 1

        if len(playable_dominoes) == 0:
            heuristic -= 1

        for player in PLAYERS:
            if player != computer:
                if len(player.dominoes) >= len(computer.dominoes):
                    heuristic += 1
                else:
                    heuristic -= 1

        for player in PLAYERS:
            if player != computer:
                if player.points <= computer.points:
                    heuristic += 1
                else:
                    heuristic -= 1

        for domino in computer.dominoes:
            if domino.acotao:
                heuristic -= 1
            else:
                heuristic += 1

        return heuristic

    def is_empty(self):
        return len(self.fake_table) == 0

    def __repr__(self):
        return str(self.fake_table)


class GameManager():
    def __init__(self):
        self.You_Win = False
        self.In_Game = False
        self.real = False

        self.count_points = True
        self.teams = False

        self.possibility_of_lock_the_game = False
        self.locked = False
        self.winner = None

    def check_game_status(self, last_turn):
        players_without_dominos = 0
        terminal_val = None

        for player in PLAYERS:
            winner = self.check_for_winner(player)

            if winner:
                terminal_val = player
                self.win(player)
                
            if self.possibility_of_lock_the_game:
                can_play = self.check_player_dominoes(player)
                if can_play:
                    continue
                else:
                    players_without_dominos += 1

            if players_without_dominos >= PLAYERS_NUM and self.check_table_dominoes():
                result = self.game_locked(last_turn)
                return result * np.inf

        if terminal_val == PLAYERS[last_turn]:
            return 1 * np.inf
        elif terminal_val is not None:
            return -1 * np.inf
        else:
            return terminal_val

    def game_locked(self, last_turn):
        self.locked = True
        player1 = PLAYERS[last_turn].count_tiles()
        try:
            player2 = PLAYERS[last_turn + 1].count_tiles()
        except:
            player2 = PLAYERS[0].count_tiles()

        if player1 < player2:
            self.win(PLAYERS[last_turn])
            return 1
        
        elif player1 > player2:
            try:
                self.win(PLAYERS[last_turn + 1])
                return -1
            
            except:
                self.win(PLAYERS[0])
                return -1
            
        else:
            try:
                self.win(PLAYERS[last_turn + 1])
                return -1
            
            except:
                self.win(PLAYERS[0])
                return -1  

    def check_table_dominoes(self):
        left = table.table_dominoes[0].vals[0]
        right = table.table_dominoes[-1].vals[-1]
        for domino in table.dominoes:
            if left in domino.vals:
                return False
            if right in domino.vals:
                return False
        
        return True

    def check_player_dominoes(self, player):
        if len(table.table_dominoes) == 0:
            return True

        left = table.table_dominoes[0].vals[0]
        right = table.table_dominoes[-1].vals[-1]
        for domino in player.dominoes:
            if left in domino.vals:
                return True
            if right in domino.vals:
                return True

        return False

    def check_for_winner(self, player):
        if len(player.dominoes) == 0:
            return True

    def win(self, winner):
        if self.real:
            self.winner = winner
            self.You_Win = True
            self.In_Game = False

            for player in PLAYERS:
                self.winner.add_points(player.count_tiles())

            if table.capicua() and self.locked != True and self.winner.count_tiles() == 0:
                self.winner.add_points(30)

    def new_game(self):
        self.In_Game = True
        self.You_Win = False
        self.winner = None

    def clear_scores(self):
        self.new_game()

        for player in PLAYERS:
            player.clear_points()


class MinimaxSolver():
    def __init__(self, max_depth=6, ts=None, max_time=None, timeit=False):
        self.max_depth = max_depth
        self.max_time = max_time
        self.timeit = timeit
        self.ts = ts

    def solve(self, state, computer_idx):
        max_child, _ = self.__maximize(state, -np.inf, np.inf, computer_idx, 0)
        return max_child

    def __maximize(self, state, alpha, beta, computer_idx, depth):
        if self.timeit:
            if time.time() - self.ts >= self.max_time:
                return (None, -np.inf)

        terminal_val = gameManager.check_game_status(computer_idx)
        if terminal_val is not None:
            return (None, terminal_val)
        
        if depth >= self.max_depth:
            return (None, state.heuristic(computer_idx))
        
        max_child, max_utility = (None, -np.inf)
        for child in state.childrens(computer_idx):
            _, utility = self.__minimize(child, alpha, beta, computer_idx, depth + 1)

            if utility > max_utility:
                max_child, max_utility = child, utility

            if utility >= beta:
                break

            alpha = max(alpha, max_utility)
        return max_child, max_utility
    
    def __minimize(self, state, alpha, beta, computer_idx, depth):
        if self.timeit:
            if time.time() - self.ts >= self.max_time:
                return (None, -np.inf)

        terminal_val = gameManager.check_game_status(computer_idx)
        if terminal_val is not None:
            return (None, terminal_val)
        
        if depth >= self.max_depth:
            return (None, state.heuristic(computer_idx))
        
        min_child, min_utility = (None, np.inf)
        for child in state.childrens(computer_idx):
            _, utility = self.__maximize(child, alpha, beta, computer_idx, depth + 1)

            if utility < min_utility:
                min_child, min_utility = child, utility

            if utility < alpha:
                break

            beta = min(beta, min_utility)
        return min_child, min_utility


def update_layers():
    BACKGROUND = pygame.image.load(f"assets/Table({PLAYERS_NUM}).png").convert_alpha()
    WINDOW.blit(BACKGROUND, (0, 0))
    
    WINDOW.blit(player_to_play, PLAYER_NUM_pos)
    WINDOW.blit(PLAYER__, PLAYER__pos)

    try:
        WINDOW.blit(can_play, can_play_pos)
        WINDOW.blit(turn, turn_pos)
    except:
        pass

    table.players_dominoes()

    for object in OBJECTS:
        if object.layer not in LAYERS:
            LAYERS[object.layer] = Layer()

        LAYERS[object.layer].add(object)

    for _, layer in LAYERS.items():
        layer.update()
        layer.draw(WINDOW)

    pygame.display.flip()
    pygame.display.update() 


def add_domino_to_layers(domino):
    if domino not in OBJECTS:
        domino.change_orientation_sprite()
        OBJECTS.append(domino)
        domino.in_screen = True
        domino.update()


def domino_sound():
    dominoNum = random.randint(0, 26)
    DOMINO_SOUND =  pygame.mixer.Sound(f'assets/Audio/domino{dominoNum}.wav')
    DOMINO_SOUND.play()


def run():
    global gameManager
    global can_play
    global player
    global table
    global turn
    global TURN

    table = Table()
    table.start_game()
    gameManager = GameManager()
    gameManager.new_game()

    clock = pygame.time.Clock()
    max_time = 0.6
    turn = None
    TURN = 0

    can_play = pygame.image.load(f"assets/Dominos (Interface)/0.png").convert_alpha()
    for turnNum in range(PLAYERS_NUM):
        try:
            if PLAYERS[turnNum].manual:
                table.draw_player_dominoes(turnNum)
                table.draw_player_number(turnNum)
        
        except:
            pass

    while gameManager.In_Game:
        table.turn = TURN
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        if PLAYERS[TURN].manual:
            turn = pygame.image.load(f"assets/Dominos (Interface)/Tu Turno.png").convert_alpha()
            played = table.player_plays(TURN)
            turn = pygame.image.load(f"assets/Dominos (Interface)/0.png").convert_alpha()

        else:
            state = Fake_Table(state=table.table_dominoes)
            best_state = None

            ts = time.time()
            minimax_solver = MinimaxSolver(max_time=max_time, ts=ts)
            for depth in range(1, 20):
                minimax_solver.max_depth = depth
                best_state = minimax_solver.solve(state, TURN)

                if time.time() - ts >= max_time:
                    break
            
            if best_state is not None:
                domino = np.array([domino for domino in best_state.fake_table if domino not in state.fake_table])
                idx = np.where(best_state.fake_table == domino)[0]
                
                domino_idx = int(np.where(PLAYERS[TURN].dominoes == domino)[0])
                domino_to_play = PLAYERS[TURN].dominoes[domino_idx]

                if len(state.fake_table) == 0:
                    table.add_domino_to_table(domino_to_play, "none")

                elif idx <= 0 and len(state.fake_table) != 0:
                    table.add_domino_to_table(domino_to_play, "left")

                elif idx >= 1 and len(state.fake_table) != 0:
                    table.add_domino_to_table(domino_to_play, "right")

                PLAYERS[TURN].dominoes = np.delete(PLAYERS[TURN].dominoes, np.where(PLAYERS[TURN].dominoes == domino))
                add_domino_to_layers(domino_to_play)
                played = True
            
            elif best_state is None and len(table.dominoes) != 0:
                PLAYERS[TURN].add_domino(table.draw_random())
                #EXTRA_DOMINO_SOUND.play()
                table.extra_domino = True

                if len(table.table_dominoes) < PLAYERS_NUM and PLAYERS[TURN].first_pick:
                    try:
                        PLAYERS[TURN - 1].add_points(30)
                    except:
                        PLAYERS[-1].add_points(30)

                    PLAYERS[TURN].first_pick = False

                continue

            elif best_state is None and len(table.dominoes) == 0:
                if PLAYERS_NUM == 2:
                    if len(table.table_dominoes) < PLAYERS_NUM:
                        try: PLAYERS[TURN - 1].add_points(30)
                        except: PLAYERS[-1].add_points(30)

                played = True

            update_layers()

        if played == -1:
            break

        gameManager.real = True
        gameManager.check_game_status(TURN)
        gameManager.real = False

        if played:
            table.extra_domino = False
            played = False
            TURN += 1

            time.sleep(SLEEP_TIME)
            if TURN >= PLAYERS_NUM:
                TURN = 0

        if len(table.dominoes) == 0:
            gameManager.possibility_of_lock_the_game = True
        
        update_layers()

    if gameManager.You_Win:
        GAME_FINISHED_SOUND.play()
        text = font.render(f"Jugador #{gameManager.winner.num + 1} gano la partida", True, text_color, bck_color)
        
        textRect = text.get_rect()
        textRect.center = (WIDTH // 2, 66)

        WINDOW.blit(text, textRect)

        y_padding = 120
        for player in PLAYERS:
            points = font.render(f"Dominos del jugador #{player.num + 1} en total: {player.count_tiles()}", True, text_color, bck_color)
        
            textRect2 = points.get_rect()
            textRect2.center = (WIDTH // 2, y_padding)
            y_padding += 30

            WINDOW.blit(points, textRect2)

        y_padding += 30
        if table.capicua() and gameManager.winner.count_tiles() == 0:
            capicua = font.render(f"Jugador #{gameManager.winner.num + 1} hizo capicua! (Son +30)", True, text_color, bck_color)
        
            textRect3 = capicua.get_rect()
            textRect3.center = (WIDTH // 2, y_padding)

            WINDOW.blit(capicua, textRect3)
        
        elif gameManager.locked and gameManager.winner.count_tiles() != 0:
            trancao = font.render(f"Jugador #{gameManager.winner.num + 1} ha trancado el juego!", True, text_color, bck_color)
        
            textRect3 = trancao.get_rect()
            textRect3.center = (WIDTH // 2, y_padding)

            WINDOW.blit(trancao, textRect3)

        pygame.display.update()
        time.sleep(SLEEP_TIME*24)

    OBJECTS, LAYERS = table.repeat_game()
    return OBJECTS, LAYERS


def intro():
    skip = False
    for i in range(2, 10):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN and event.key == K_ESCAPE:
                skip = True
                break

        if skip:
            break

        intro = pygame.image.load(f"assets/Dominos (Interface)/Intro/dominoIntro{i}.png").convert_alpha()
            
        WINDOW.blit(intro, (0, 0))
        pygame.display.flip()
        pygame.display.update()
            
        time.sleep(SLEEP_TIME*0.175)

    if skip != True:
        time.sleep(SLEEP_TIME*3.6)


def main():
    global OBJECTS, LAYERS, PLAYERS_NUM, WINDOW, SLEEP_TIME, PLAYERS, last_players_num
    intro()

    while True:
        OBJECTS, LAYERS = run()
        update_layers()

        if last_players_num == PLAYERS_NUM:
            text = font.render('Puntos', True, text_color, bck_color)
            
            textRect = text.get_rect()
            textRect.center = (WIDTH // 2, 66)

            WINDOW.blit(text, textRect)
            y_padding = 100

            for player in PLAYERS:
                points = font.render(f"Jugador #{player.num + 1}: {player.points}", True, text_color, bck_color)
            
                textRect2 = points.get_rect()
                textRect2.center = (WIDTH // 2, y_padding)
                y_padding += 30

                WINDOW.blit(points, textRect2)

            pygame.display.update()
            time.sleep(SLEEP_TIME*24)

        if last_players_num != PLAYERS_NUM:
            PLAYERS = [Player(num) for num in range(PLAYERS_NUM)]
            last_players_num = PLAYERS_NUM

            if PLAYERS_NUM == 2:
                optionNum = random.randint(0, 1)

                if optionNum == 0:
                    player = PLAYERS[0]
                    PLAYERS[1].change_auto()
                
                else:
                    player = PLAYERS[1]
                    PLAYERS[0].change_auto()
            
            if PLAYERS_NUM == 3:
                optionNum = random.randint(0, 2)

                if optionNum == 0:
                    player = PLAYERS[0]
                    PLAYERS[1].change_auto()
                    PLAYERS[2].change_auto()
                
                elif optionNum == 1:
                    player = PLAYERS[1]
                    PLAYERS[0].change_auto()
                    PLAYERS[2].change_auto()

                else:
                    player = PLAYERS[2]
                    PLAYERS[1].change_auto()
                    PLAYERS[0].change_auto()
            
            if PLAYERS_NUM == 4:
                optionNum = random.randint(0, 3)

                if optionNum == 0:
                    player = PLAYERS[0]
                    PLAYERS[1].change_auto()
                    PLAYERS[2].change_auto()
                    PLAYERS[3].change_auto()
                
                elif optionNum == 1:
                    player = PLAYERS[1]
                    PLAYERS[0].change_auto()
                    PLAYERS[2].change_auto()
                    PLAYERS[3].change_auto()

                elif optionNum == 2:
                    player = PLAYERS[2]
                    PLAYERS[1].change_auto()
                    PLAYERS[0].change_auto()
                    PLAYERS[3].change_auto()

                else:
                    player = PLAYERS[3]
                    PLAYERS[1].change_auto()
                    PLAYERS[2].change_auto()
                    PLAYERS[0].change_auto()
        
        # await asyncio.sleep(0)
        pygame.display.flip()
        pygame.display.wait(1000)


main()