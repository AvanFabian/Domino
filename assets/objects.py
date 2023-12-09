import numpy as np
import pygame
import os
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from constants import *

# domino_area = pygame.Rect(-1257, -637, 58, 96)

# Global dictionary to store loaded textures
texture_cache = {}

def scale_texture(scaleX, scaleY):
    glPushMatrix()
    glScalef(scaleX, scaleY, 0)
    glPopMatrix()

def rotate_texture(angle):
    glPushMatrix()
    glRotatef(angle, 0, 0, 0) 
    glPopMatrix()

def convert_coordinates(mouse_coord):
    opengl_x = (mouse_coord[0] - WIDTH / 2) * (2 / WIDTH) * 1400
    # print(f"mouse_coord[0] - WIDTH / 2: {mouse_coord[0] - WIDTH / 2}")
    opengl_y = (HEIGHT / 2 - mouse_coord[1]) * (2 / HEIGHT) * 800
    # print(f"opengl_x, opengl_y: ({opengl_x}, {opengl_y})")
    return opengl_x, opengl_y


class GameObject(pygame.sprite.Sprite):
    def __init__(self, x=0, y=0, layer=0, x_scale=1, y_scale=1, orientation=0, img_path=os.path.join("assets", "empty.png"), img_width=0, img_height=0):
        super().__init__()
        self.x = x
        self.y = y
        self.layer = layer
        self.x_scale = x_scale
        self.y_scale = y_scale
        self.object_rect = None
        self.position = np.array([x, y])
        self.orientation = orientation
        self.load_image(img_path)
        self.image_path = img_path
        self.width = img_width
        self.height = img_height
        self.blank_path = os.path.join("assets", "Dominos (Interface)", "0.png")
        self.change_vals = False
    
    def load_texture(self, image_path):
        global img_width, img_height
        textureSurface = pygame.image.load(image_path).convert_alpha()
        textureData = pygame.image.tostring(textureSurface, "RGBA", 1)
        img_width = textureSurface.get_width()
        img_height = textureSurface.get_height()
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img_width, img_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, textureData)

        # glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

        return texture

    def display_normal_texture(self, posX, posY, scaleX, scaleY, jenis_texture):
        glBindTexture(GL_TEXTURE_2D, jenis_texture)
        glPushMatrix()
        glTranslatef(posX, posY, 1.0)  # Adjust the z-coordinate to place the button in front of the background
        glScalef(scaleX, scaleY, 0) 
        cube()
        glPopMatrix()

    def load_image(self, path):
        self.change_vals = False

        try:
            self.image = self.load_texture(path)
            self.display_normal_texture(self.x, self.y, self.x_scale, self.y_scale, self.image)
        except:
            path = change_vals(path, 22, 24)
            self.image = self.load_texture(path)
            self.change_vals = True

        self.width = img_width
        self.height = img_height
        scale_texture(self.width*self.x_scale, self.height*self.y_scale)
        rotate_texture(self.orientation)
        self.object_rect = pygame.Rect((self.x-(self.width)), (self.y-(self.height)), (self.width*2), (self.height*2))

        if self.change_vals:
            self.change_orientation(180)

    def update_image(self, path):
        self.image = self.load_texture(path)

    def refresh_sprite(self):
        scale_texture(self.width*self.x_scale, self.height*self.y_scale)
        # self.object_rect = img_rect
        self.object_rect = pygame.Rect((self.x-(self.width/2)), (self.y-(self.height/2)), self.width, self.height)

    def update(self):
        self.refresh_sprite()
        # self.object_rect.center = (self.x, self.y)
        self.object_rect.center = (self.x, self.y)

    def is_colliding(self, position):
        if self.object_rect.collidepoint(position):
            print("colliding!")
            return True
        else:
            # print("not colliding")
            return False

    def change_sprite(self, path):
        self.load_image(path)
    
    def hide(self):
        self.load_image(self.blank_path)

    def show(self):
        self.load_image(self.image_path)

    def add_position(self, x, y):
        self.position = np.array([x, y])
        print(f"position in add_position at objects.py: {self.position}")
        self.x = x
        self.y = y

    def change_orientation(self, new_orientation):
        self.orientation = new_orientation
        rotate_texture(self.orientation)
        self.object_rect = pygame.Rect((self.x-(self.width/2)), (self.y-(self.height/2)), self.width, self.height)

    def give_rect(self):
        return self.object_rect
    
    def give_position(self):
        return self.x, self.y

    def destroy(self):
        pass


class Domino(GameObject):
    def __init__(self, vals:list, **kwargs):
        self.vals = np.array(vals)
        self.placed = False
        self.empty = False
        self.extra = False
        self.jump = True

        if vals[0] == vals[1]:
            self.acotao = True
        else:
            self.acotao = False

        if vals == [7, 7]:
            self.in_screen = True
            self.path = "_.png"
            self.extra = True

        else:
            self.path = f"{vals[0]}-{vals[1]}.png"
            # print(f"path in objects.py line 211: {self.path}")
            self.in_screen = False

        super().__init__(img_path=os.path.join("assets", "Dominos (Game)", self.path), x_scale=56.75, y_scale=96.0, orientation=0, **kwargs)
        self.object_rect = super().give_rect()

    def __copy__(self):
        new_instance = Domino(list(self.vals))
        new_instance.placed = self.placed
        new_instance.empty = self.empty
        new_instance.extra = self.extra
        new_instance.jump = self.jump
        new_instance.acotao = self.acotao
        new_instance.in_screen = self.in_screen
        new_instance.path = self.path
        new_instance.object_rect = self.object_rect

        return new_instance

    def add_position(self, x, y): # nampilin domino yang dipilih
        super().add_position(x, y)

    def view_horizontal(self):
        super().change_orientation(90)

    def view_vertical(self):
        super().change_orientation(0)

    def change_orientation_sprite(self):
        super().change_orientation(180)

    def change_orientation_vals(self):
        self.vals = np.array([self.vals[1], self.vals[0]])
        self.change_orientation_sprite()

    def change_vals(self):
        self.vals = np.array([self.vals[1], self.vals[0]])

    def domino_placed(self):
        self.placed = True

    def show(self): # nampilin domino yang di klik ke tengah layar
        self.in_screen = True
        super().show()

    def hide(self):
        self.in_screen = False
        super().hide()

    def update(self):
        x, y = super().give_position()
        mouse_position = pygame.mouse.get_pos()
        GlCoord = convert_coordinates(mouse_position)
        # print(f"GlCoord: {GlCoord}")
        if super().is_colliding(GlCoord) and self.placed == False and self.in_screen == True:
            # print("UPDATE DI COLLIDING DOMINO")
            if self.empty:
                self.placed = True
                self.jump = False

            if self.jump:
                print("NGEHOVER DI UPDATE")
                self.on_hover()
      
        else:
            # print("UPDATE DI ELSE DOMINO")
            super().update()
            self.jump = True

        # print("UPDATE DI UPDATE")
        self.x, self.y = x, y

    def extra_dominoes_is_empty(self):
        self.empty = True

    def on_hover(self): # on_hover = ketika domino di hover
        print("on_hover domino")
        pixels_to_move = 20 # pixels to move is the amount of pixels the domino will move when hovered
        self.y -= pixels_to_move
        
        self.image = scale_texture(self.width*self.x_scale, self.height*self.y_scale)

        print(f"self.object_rect.height: {self.object_rect.height}")
        new_height = self.object_rect.height + pixels_to_move
        self.object_rect.height = new_height
        self.object_rect.center = (self.x, self.y)
        self.jump = False

    def sum_vals(self):
        return int(self.vals[0]) + int(self.vals[1])

    def click_me(self):
        if self.in_screen:
            mouse_position = pygame.mouse.get_pos()
            # print(f"mouse_position: {mouse_position}")
            GlCoord = convert_coordinates(mouse_position)
            if self.object_rect.collidepoint(GlCoord):
                print("domino clicked!")
                return True
            else:
                return False
    def __repr__(self):
        return str(list(self.vals))


class Button(GameObject):
    def __init__(self, path):
        self.path1 = path
        self.path2 = path.replace("1", "2")
        self.arrow = False
        self.position = None
        self.in_screen = False

        super().__init__(img_path=os.path.join("assets", "Dominos (Interface)", self.path1), x_scale=20, y_scale=20, orientation=0)
        self.object_rect = super().give_rect()

    def add_position(self, x, y):
        super().add_position(x, y)

    def change_orientation_sprite(self):
        super().change_orientation(180)

    def activate(self):
        self.in_screen = True
        super().show()

    def deactivate(self):
        self.in_screen = False
        super().hide()

    def update(self):
        mouse_position = pygame.mouse.get_pos()
        GlCoord = convert_coordinates(mouse_position)
        if self.in_screen:
            if super().is_colliding(GlCoord):
                super().change_sprite(os.path.join("assets", "Dominos (Interface)", self.path2))

            else:
                super().change_sprite(os.path.join("assets", "Dominos (Interface)", self.path1))  
            
        super().update()

    def click_me(self):
        if self.in_screen:
            mouse_position = pygame.mouse.get_pos()
            GlCoord = convert_coordinates(mouse_position)
            if self.object_rect.collidepoint(GlCoord):
                print("button clicked!")
                return True
            else:
                return False

class Player:
    def __init__(self, num, manual=True):
        self.dominoes = np.array([])
        self.first_pick = True
        self.manual = manual
        self.points = 0
        self.num = num

    def add_domino(self, domino):
        # print(f"domino onjects 355: {domino}")
        self.dominoes = np.append(self.dominoes, domino)

    def remove_all(self):
        self.dominoes = np.array([])

    def count_tiles(self):
        sum_of_dominoes = 0

        for domino in self.dominoes:
            sum_of_dominoes += domino.sum_vals()

        return sum_of_dominoes

    def add_points(self, points):
        self.points += points 

    def clear_points(self):
        self.points = 0

    def change_manual(self):
        self.manual = True

    def change_auto(self):
        self.manual = False

    def __repr__(self):
        return f"\nPlayer #{self.num} (Manual: {self.manual})\nDominoes: {self.dominoes}\n"


def change_vals(path, idx1, idx2):
    characters = list(path)

    characters[idx1], characters[idx2] = characters[idx2], characters[idx1]
    new_path = ''.join(characters)

    return new_path