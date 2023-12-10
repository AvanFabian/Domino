from assets.objects import Domino, Player, Button
from pygame.sprite import Group as Layer
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from constants import *
import numpy as np
import random
import pygame
import time
import sys

# Global dictionary to store loaded textures
texture_cache = {}

# digunakan untuk memproses gambar menjadi texture
def load_texture(image_path):
        # Check if the texture is already in the cache
    if image_path in texture_cache:
        return texture_cache[image_path]
    
    textureSurface = pygame.image.load(image_path).convert_alpha()
    textureData = pygame.image.tostring(textureSurface, "RGBA", 1)

    # mendapatkan ukuran texture
    width = textureSurface.get_width()
    height = textureSurface.get_height()

    textureId = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, textureId)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, textureData)

    # glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

    # Add the texture to the cache
    texture_cache[image_path] = textureId

    return textureId

def render_text(text, font, text_color, background_color):
    text_surface = font.render(text, True, text_color, background_color)
    text_data = pygame.image.tostring(text_surface, "RGBA", 1)
    width, height = text_surface.get_width(), text_surface.get_height()
    print(f"width: {width}, height: {height}")

    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexImage2D(
        GL_TEXTURE_2D,
        0,
        GL_RGBA,
        width,
        height,
        0,
        GL_RGBA,
        GL_UNSIGNED_BYTE,
        text_data,
    )
    return texture, width, height

def display_text(posX, posY, scaleX, scaleY, texture, width, height):
    glBindTexture(GL_TEXTURE_2D, texture)
    glEnable(GL_TEXTURE_2D)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex3f(posX, posY, 0)
    glTexCoord2f(1, 0)
    glVertex3f(posX + scaleX, posY, 0)
    glTexCoord2f(1, 1)
    glVertex3f(posX + scaleX, posY + scaleY, 0)
    glTexCoord2f(0, 1)
    glVertex3f(posX, posY + scaleY, 0)
    glEnd()
    glDisable(GL_TEXTURE_2D)

def display_bg_texture(path):
    jenis_texture = load_texture(path)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, jenis_texture)
    glPushMatrix()
    glTranslatef(0.0, 0.0, 0.0)  # Adjust the z-coordinate to place the button in front of the background
    glScalef(TableXSize, TableYSize, 0)  # Scaling background hingga sesuai dengan ukuran window
    cube()
    glPopMatrix()

# digunakan untuk menampilkan semua texture selain BACKGROUND
# def display_normal_texture(posX, posY, scaleX, scaleY, jenis_texture):
#     glBindTexture(GL_TEXTURE_2D, jenis_texture)
#     glPushMatrix()
#     glTranslatef(posX, posY, 1.0)  
#     glScalef(scaleX, scaleY, 0) 
#     cube()
#     glPopMatrix()

def display_normal_texture(posX, posY, scaleX, scaleY, path):
    jenis_texture = load_texture(path)
    glBindTexture(GL_TEXTURE_2D, jenis_texture)
    glPushMatrix()
    glTranslatef(posX, posY, 1.0)  
    glScalef(scaleX, scaleY, 0) 
    cube()
    glPopMatrix()

# Function to unload a texture
def unload_texture(image_path):
    if image_path in texture_cache:
        glDeleteTextures([texture_cache[image_path]])
        del texture_cache[image_path]


# digunakan untuk men-setting layar + variabel-variable yang dibutuhkan
def display_init():
    # buat global variabel
    global PLAYERS, WINDOW, WIDTH, HEIGHT, BACKGROUND, PLAYER__, PLAYER__pos, PLAYER_NUM_pos, can_play_pos, turn_pos, player, SLEEP_TIME, PLAYERS_NUM, last_players_num, FPS, text_color, bck_color, font, GAME_FINISHED_SOUND, \
    EXTRA_DOMINO_SOUND, BUTTOM_SOUND, OBJECTS, LAYERS, PLAYER__scale, PLAYER_NUM_scale, can_play_scale, turn_pos_scale, ICON, FULLSCREEN, EXIT, REPEAT, PASS
    # IKI AWAS BUGGG
    material_ambient = (0.1, 0.1, 0.1, 1.0)
    material_diffuse = (0.7, 0.7, 0.7, 1.0)
    material_specular = (0.5, 0.5, 0.5, 1)
    pygame.init()
    screen_size = (WIDTH, HEIGHT)
    WINDOW = pygame.display.set_mode(screen_size, DOUBLEBUF | OPENGL)
    print(f"Window: {WINDOW}")
    

    pygame.display.set_caption('TheMino: Ordinary Domino Game')
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_BLEND)

    # Set material properties
    glMaterialfv(GL_FRONT, GL_AMBIENT, material_ambient)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, material_diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, material_specular)

    # Memasang Ortho
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(-1400, 1400, -800, 800)
    glMatrixMode(GL_MODELVIEW)
    glLightfv(GL_LIGHT0, GL_POSITION, (1, 1, -1, 0))


    ICON = pygame.image.load("assets/DominoIcon.png").convert_alpha()
    # ICON = load_texture("assets/DominoIcon.png")
    pygame.display.set_icon(ICON)

    PLAYERS_NUM = 2
    last_players_num = PLAYERS_NUM

    BACKGROUND = f"assets/Table({PLAYERS_NUM}).png" # PRoses gambar bg menjadi texture

    PLAYER__ = f"assets/Dominos (Interface)/jugador#.png" # PRoses gambar player menjadi texture

    SLEEP_TIME = .16
    PLAYER__scale = (185, 75) # skala teks player
    PLAYER__pos = (-1185, -415) # posisi teks player
    PLAYER_NUM_scale = (55, 67) # skala teks jumlah kartu pemain
    PLAYER_NUM_pos = (-925, -415) # posisi teks jumlah kartu pemain
    can_play_pos = (-725, -415)
    can_play_scale = (125, 55)
    turn_pos = (0, 725)
    turn_pos_scale = (125, 60)

    # WINDOW.blit(BACKGROUND, (0, 0))
    display_bg_texture(BACKGROUND)
    # WINDOW.blit(PLAYER__, PLAYER__pos)
    display_normal_texture(PLAYER__pos[0], PLAYER__pos[1], PLAYER__scale[0], PLAYER__scale[1], PLAYER__)
    unload_texture(PLAYER__)

    OBJECTS = [] # list yang berisi semua objek yang ada di game
    LAYERS = {0: Layer()} # dictionary yang berisi semua layer yang ada di game

    PLAYERS = [Player(num) for num in range(PLAYERS_NUM)] # list yang berisi semua pemain yang ada di game
    #Player
    player = PLAYERS[0] # pemain yang sedang bermain

    #computer
    #PLAYERS[0].change_auto()
    PLAYERS[1].change_auto() # mengubah pemain ke mode komputer
    #PLAYERS[2].change_auto()
    #PLAYERS[3].change_auto()

    FPS = 60 # frame per second

    text_color = (59, 32, 39) # warna teks
    bck_color = (255, 194, 161) # warna background

    # X = WIDTH # lebar window
    # Y = HEIGHT # tinggi window

    font = pygame.font.Font('assets/alagard.ttf', 32) # jenis font

    GAME_FINISHED_SOUND =  pygame.mixer.Sound('assets/Audio/gameFinished.wav') # suara yang akan diputar ketika game selesai
    EXTRA_DOMINO_SOUND =  pygame.mixer.Sound('assets/Audio/newDomino.wav') # suara yang akan diputar ketika pemain mengambil kartu tambahan
    BUTTOM_SOUND =  pygame.mixer.Sound('assets/Audio/Buttom.wav') # suara yang akan diputar ketika pemain menekan tombol

class Table():
    def __init__(self): # fungsi yang akan dijalankan ketika objek Table dibuat, Table adalah objek yang merepresentasikan meja permainan
        self.turn = 0 # giliran pemain
        self.spacing = 145 # jarak antar kartu (TAK UBAH DARI SEBELUMNYA 96)
        self.first_game = True # atribut yang menandakan apakah game ini adalah game pertama atau tidak
        self.dominoes = np.array([], dtype=object) # list yang berisi semua kartu domino yang ada di game, dtype=object digunakan agar list dapat menyimpan objek diantaranya (string, integer, float, array lain, dll)
        self.table_dominoes = np.array([], dtype=object) # list yang berisi semua kartu domino yang ada di meja

        self.left_iterator = 0 # iterator yang menandakan posisi kartu domino yang akan ditaruh di sisi kiri meja
        self.right_iterator = 0 # iterator yang menandakan posisi kartu domino yang akan ditaruh di sisi kanan meja
        self.left_positions = [] # list yang berisi semua posisi kartu domino yang akan ditaruh di sisi kiri meja
        self.right_positions = [] # list yang berisi semua posisi kartu domino yang akan ditaruh di sisi kanan meja

        self.last_player = None # pemain yang terakhir kali bermain
        self.extra_domino = False # atribut yang menandakan apakah pemain mengambil kartu tambahan atau tidak
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
                # print(f"self.dominoes: {self.dominoes[-1]}")

        for player in PLAYERS:
            for _ in range(7):
                player.add_domino(self.draw_random())
    
    def draw_random(self):
        domino = np.random.choice(self.dominoes)
        self.dominoes = np.delete(self.dominoes, np.where(self.dominoes == domino))
        return domino
    
    def extra_domino_sprite(self):
        # extra_domino = pygame.image.load(f"assets/Dominos (Interface)/+.png").convert_alpha()
        extra_domino = f"assets/Dominos (Interface)/+.png"
        # WINDOW.blit(extra_domino, (self.extra_x, self.extra_y))
        # print(f"line 265:\nself.extra_x: {self.extra_x}, self.extra_y: {self.extra_y}")
        display_normal_texture(self.extra_x, self.extra_y, 35, 35, extra_domino)
        unload_texture(extra_domino)

    def draw_player_number(self, player_number):
        global player_to_play
        # player_to_play = pygame.image.load(f"assets/Dominos (Interface)/{player_number + 1}p.png").convert_alpha()
        player_to_play = f"assets/Dominos (Interface)/{player_number + 1}p.png"
        # WINDOW.blit(player_to_play, PLAYER_NUM_pos
        display_normal_texture(PLAYER_NUM_pos[0], PLAYER_NUM_pos[1], PLAYER_NUM_scale[0], PLAYER_NUM_scale[1], player_to_play)
        unload_texture(player_to_play)
        update_layers()

    def draw_player_dominoes(self, player_idx):
        if PLAYERS[player_idx].manual:
            x_padding = 136.5
            y_padding = 260

            x, y = -1275, -637
            aux = 1

            for domino in PLAYERS[player_idx].dominoes:
                if domino not in OBJECTS:
                    OBJECTS.append(domino)

                domino.add_position(x, y)
                domino.show()

                if aux == 7:
                    x, y = -1275, -637
                    y += y_padding
                    aux = 0

                    y_padding += 50
                
                else:
                    x += x_padding
                    # pass

                aux += 1 

    def erase_player_dominoes(self, player_idx):
        players = [index for index, player in enumerate(PLAYERS) if index != player_idx]

        for player in players:
            if PLAYERS[player].manual:
                for domino in PLAYERS[player].dominoes:
                    domino.hide()

    def draw_extra_dominoes(self):
        self.extra_dominoes = Domino([7, 7], x=-305, y=-637) 
        OBJECTS.insert(0, self.extra_dominoes)

    def hide_extra_dominoes(self):
        self.extra_dominoes.extra_dominoes_is_empty()
        self.extra_dominoes.hide()

    def is_empty(self):
        return len(self.table_dominoes) == 0
    
    def create_right_positions(self):
        right_x, right_y = 145, 0

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
        left_x, left_y = -145, 0

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
        print(f"left: {left}")
        print(f"right: {right}")

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
                domino.add_position(0, 0)

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
        if self.left_iterator >= 85 and self.left_iterator <= 87:
            domino.change_orientation_sprite()
            domino.view_horizontal()

        elif self.left_iterator >= 87 and self.left_iterator <= 89:
            domino.change_orientation_sprite()

        elif self.left_iterator >= 89 and self.left_iterator <= 95:
            domino.view_horizontal()
        
        elif self.left_iterator >= 95:
            domino.view_vertical()
            
        self.table_dominoes = np.insert(self.table_dominoes, 0, domino)
        x, y = self.left_positions[self.left_iterator][0], self.left_positions[self.left_iterator][1]
        domino.add_position(x, y)

        self.left_iterator += 1

    # def right_placement(self, domino):
    #     domino.change_orientation_sprite()
    #     if self.right_iterator >= 85 and self.right_iterator <= 88:
    #         domino.change_orientation_sprite()
    #         domino.view_horizontal()

    #     elif self.right_iterator >= 88 and self.right_iterator <= 90:
    #         domino.change_orientation_sprite()

    #     elif self.right_iterator >= 90 and self.right_iterator <= 95:
    #         domino.view_horizontal()

    #     elif self.right_iterator >= 95 and self.right_iterator <= 101:
    #         domino.change_orientation_sprite()
        
    #     elif self.right_iterator >= 101 and self.right_iterator <= 103:
    #         domino.view_horizontal()

    #     elif self.right_iterator >= 103:
    #         domino.view_vertical()

    #     self.table_dominoes = np.append(self.table_dominoes, domino)
    #     x, y = self.right_positions[self.right_iterator][0], self.right_positions[self.right_iterator][1]
    #     domino.add_position(x, y)

    #     self.right_iterator += 1

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
        # sisa domino pemain
        x, y = 1260, 715
        x_scale, y_scale = 85, 22
        # nomor player
        num_x, num_y = 1140, 715
        num_x_scale, num_y_scale = 30, 45
        # tanda panah giliran player
        turn_x, turn_y = 960, 715
        turn_x_scale, turn_y_scale = 65, 35
        sprite_added = True

        for player in PLAYERS:
            dominoes_amount = len(player.dominoes)

            if dominoes_amount >= 7:
                dominoes_amount = 7
            elif dominoes_amount == 6:
                x_scale = 75
                y_scale = 22
            elif dominoes_amount == 5:
                x_scale = 65
                y_scale = 20
            elif dominoes_amount == 4:
                x_scale = 55
                y_scale = 18
            elif dominoes_amount == 3:
                x_scale = 45
                y_scale = 16
            elif dominoes_amount == 2:
                x_scale = 35
                y_scale = 14
            elif dominoes_amount == 1:
                x_scale = 25
                y_scale = 12


            # num_dominoes = pygame.image.load(f"assets/Dominos (Interface)/{dominoes_amount}.png").convert_alpha()
            num_dominoes = f"assets/Dominos (Interface)/{dominoes_amount}.png"
            # player_num = pygame.image.load(f"assets/Dominos (Interface)/{player.num + 1}p.png").convert_alpha()
            player_num = f"assets/Dominos (Interface)/{player.num + 1}p.png"

            if self.turn == player.num:
                # player_turn = pygame.image.load(f"assets/Dominos (Interface)/turn.png").convert_alpha()
                player_turn = f"assets/Dominos (Interface)/turn.png"
                # self.extra_x, self.extra_y = turn_x - 46, turn_y - 6
                self.extra_x, self.extra_y = turn_x - 126, turn_y + 46
                
                if self.extra_domino and sprite_added:
                    self.extra_domino_sprite()
                    sprite_added = False

            else:
                # player_turn = pygame.image.load(f"assets/Dominos (Interface)/0.png").convert_alpha()
                player_turn = f"assets/Dominos (Interface)/0.png"

            display_normal_texture(turn_x, turn_y, turn_x_scale, turn_y_scale, player_turn)
            display_normal_texture(x, y, x_scale, y_scale, num_dominoes)
            display_normal_texture(num_x, num_y, num_x_scale, num_y_scale, player_num)
            unload_texture(num_dominoes)
            unload_texture(player_num)
            unload_texture(player_turn)

            y -= 125
            num_y -= 125
            turn_y -= 125

    def activate_arrows(self):
        if self.left_arrow_orientation:
            self.left_arrow.change_orientation_sprite()
            self.left_arrow_orientation = False

        self.right_arrow.add_position(-255, -0)
        self.left_arrow.add_position(-305, -0)
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

        x, y = -204, -712
        # x, y = -11.76, 6.75
        buttons = [PASS, REPEAT, FULLSCREEN, EXIT]

        for button in buttons:
            button.add_position(x, y)
            # y -= 0.43
            y += 51.85

        for button in buttons:
            button.show()
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
                # can_play = pygame.image.load(f"assets/Dominos (Interface)/0.png").convert_alpha()
                can_play = f"assets/Dominos (Interface)/0.png"

            else:
                # can_play = pygame.image.load(f"assets/Dominos (Interface)/no vas.png").convert_alpha()
                can_play = f"assets/Dominos (Interface)/no vas.png"
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
                                # print("Son 30!!")
                                
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

        # can_play = pygame.image.load(f"assets/Dominos (Interface)/0.png").convert_alpha()
        can_play = f"assets/Dominos (Interface)/0.png"
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

def update_layers(): # fungsi yang akan mengupdate semua layer yang ada di game
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    # BACKGROUND = load_texture(f"assets/Table({PLAYERS_NUM}).png")
    BACKGROUND = f"assets/Table({PLAYERS_NUM}).png"
    display_bg_texture(BACKGROUND)
    
    display_normal_texture(PLAYER_NUM_pos[0], PLAYER_NUM_pos[1], PLAYER_NUM_scale[0], PLAYER_NUM_scale[1], player_to_play)
    unload_texture(player_to_play)
    display_normal_texture(PLAYER__pos[0], PLAYER__pos[1], PLAYER__scale[0], PLAYER__scale[1], PLAYER__)
    unload_texture(PLAYER__)

    try:
        display_normal_texture(can_play_pos[0], can_play_pos[1], can_play_scale[0], can_play_scale[1], can_play)
        unload_texture(can_play)
        display_normal_texture(turn_pos[0], turn_pos[1], turn_pos_scale[0], turn_pos_scale[1], turn)
        unload_texture(turn)
    except:
        pass

    table.players_dominoes()

    for object in OBJECTS:
        if object.layer not in LAYERS:
            LAYERS[object.layer] = Layer()

        LAYERS[object.layer].add(object)

    for _, layer in LAYERS.items():
        # print(f"layer line 1039: {layer}")
        layer.update()
        # layer.draw(WINDOW)
        for obj in layer.sprites():
            # print(f"obj line 1043: {obj}")
            obj.show()  

    pygame.display.flip()
    # pygame.display.update() 


def add_domino_to_layers(domino):
    if domino not in OBJECTS: # jika domino belum ada di OBJECTS
        domino.change_orientation_sprite() # memutar sprite domino
        OBJECTS.append(domino) # menambahkan domino ke OBJECTS
        domino.in_screen = True # mengubah atribut in_screen menjadi True
        domino.update() 


def domino_sound():
    dominoNum = random.randint(0, 26) # berguna untuk memilih suara domino yang akan diputar
    DOMINO_SOUND =  pygame.mixer.Sound(f'assets/Audio/domino{dominoNum}.wav') # memilih suara domino yang akan diputar
    DOMINO_SOUND.play() # memutar suara domino

def run():
    global gameManager
    global can_play
    global player
    global table
    global turn
    global TURN

    # glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    table = Table()
    table.start_game()
    gameManager = GameManager()
    gameManager.new_game()

    clock = pygame.time.Clock()
    max_time = 0.6
    turn = None
    TURN = 0

    # can_play = pygame.image.load(f"assets/Dominos (Interface)/0.png").convert_alpha()
    can_play = f"assets/Dominos (Interface)/0.png"
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
            # turn = pygame.image.load(f"assets/Dominos (Interface)/Tu Turno.png").convert_alpha()
            turn = f"assets/Dominos (Interface)/Tu Turno.png"
            played = table.player_plays(TURN)
            # turn = pygame.image.load(f"assets/Dominos (Interface)/0.png").convert_alpha()
            turn = f"assets/Dominos (Interface)/0.png"

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
                add_domino_to_layers(domino_to_play) # draw domino yang diluncurkan / dipilih musuh
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
        # text = font.render(f"Pemain #{gameManager.winner.num + 1} Adalah Pemenang!", True, text_color, bck_color)
        # textRect = text.get_rect()
        # textRect.center = (WIDTH // 2, 66)
        # WINDOW.blit(text, textRect)
        # Modify this block to use PyOpenGL for rendering text
        text = f"Pemain #{gameManager.winner.num + 1} Adalah Pemenang!"
        texture, width, height = render_text(text, font, text_color, bck_color)
        display_text(WIDTH // 2 - width / 2, 66, width, height, texture, width, height)
        y_padding = 120

        for player in PLAYERS:
            # points = font.render(f"Sisa Kartu Pemain #{player.num + 1} : {player.count_tiles()}", True, text_color, bck_color)
            # textRect2 = points.get_rect()
            # textRect2.center = (WIDTH // 2, y_padding)
            # y_padding += 30
            # WINDOW.blit(points, textRect2)
            text = f"Pemain #{player.num + 1}: {player.points}"
            texture, width, height = render_text(text, font, text_color, bck_color)
            display_text(WIDTH // 2, y_padding, 1, 1, texture, width, height)
            y_padding += 30

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

        pygame.display.flip()
        # pygame.display.update()
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

        # intro = pygame.image.load(f"assets/Dominos (Interface)/Intro/dominoIntro{i}.png").convert_alpha()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        intro = f"assets/Dominos (Interface)/Intro/dominoIntro{i}.png"
            
        # WINDOW.blit(intro, (0, 0)) # (0, 0) adalah posisi x dan y dari gambar intro
        display_bg_texture(intro)
        pygame.display.flip()
        # pygame.display.update()
            
        time.sleep(SLEEP_TIME*0.175)
        # time.sleep(SLEEP_TIME*5)

    if skip != True:
        time.sleep(SLEEP_TIME*3.6)

def main():
    global OBJECTS, LAYERS, PLAYERS_NUM, WINDOW, SLEEP_TIME, PLAYERS, last_players_num
    display_init()
    intro()

    while True:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        OBJECTS, LAYERS = run()
        update_layers()

        if last_players_num == PLAYERS_NUM:
            text = font.render('Poin', True, text_color, bck_color)
            
            textRect = text.get_rect()
            textRect.center = (WIDTH // 2, 66)

            WINDOW.blit(text, textRect)
            y_padding = 100

            for player in PLAYERS:
                points = font.render(f"Pemain #{player.num + 1}: {player.points}", True, text_color, bck_color)
            
                textRect2 = points.get_rect()
                textRect2.center = (WIDTH // 2, y_padding)
                y_padding += 30

                WINDOW.blit(points, textRect2)

            pygame.display.flip()
            # pygame.display.update()
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

        pygame.display.flip()
        pygame.time.wait(10)


main()