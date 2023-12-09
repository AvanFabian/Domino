import numpy as np
import pygame
import os
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

class GameObject(pygame.sprite.Sprite):
    def __init__(self, x=0, y=0, layer=0, x_scale=1, y_scale=1, orientation=0, img_path=os.path.join("assets", "empty.png")):
        super().__init__()
        self.x = x
        self.y = y
        self.layer = layer
        self.x_scale = x_scale
        self.y_scale = y_scale
        self.position = np.array([x, y])
        self.orientation = orientation
        self.load_image(img_path)
        self.image_path = img_path
        self.blank_path = os.path.join("assets", "Dominos (Interface)", "0.png")
        self.change_vals = False

    def load_image(self, path):
        # print(f"path in load_image: {path}")
        self.change_vals = False

        try:
            self.image = pygame.image.load(path).convert_alpha()
            # self.image = load_texture(path)
        except:
            path = change_vals(path, 22, 24)
            self.image = pygame.image.load(path).convert_alpha()
            # self.image = load_texture(path)
            self.change_vals = True

        self.image = pygame.transform.scale(self.image, (self.image.get_width()*self.x_scale, self.image.get_height()*self.y_scale))
        self.image = pygame.transform.rotate(self.image, self.orientation)
        # print(f"self.image: {self.image}")
        self.rect = self.image.get_rect()
        # print(f"self.rect: {self.rect}")

        if self.change_vals:
            self.change_orientation(180)

    def update_image(self, path):
        self.image = pygame.image.load(path).convert_alpha()

    def refresh_sprite(self):
        self.image = pygame.transform.scale(self.image, (self.image.get_width()*self.x_scale, self.image.get_height()*self.y_scale))
        self.rect = self.image.get_rect()

    def update(self):
        self.refresh_sprite()
        # print(f"self.x = {self.x}, self.y = {self.y}")
        self.rect.center = (self.x, self.y) 

    def is_colliding(self, position):
        if self.rect.collidepoint(position):
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
        # print(f"position in add_position at objects.py: {self.position}")
        self.x = x
        self.y = y
        # glTranslatef(x, y, 2.5)

    def change_orientation(self, new_orientation):
        self.orientation = new_orientation
        self.image = pygame.transform.rotate(self.image, self.orientation)
        self.rect = self.image.get_rect()

    def give_rect(self):
        return self.rect
    
    def give_position(self):
        # print(f"self.x = {self.x}, self.y = {self.y}")
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
        # print(f"VALS in objects.py line 106 : {vals}")

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

        super().__init__(img_path=os.path.join("assets", "Dominos (Game)", self.path), x_scale=1, y_scale=1, orientation=0, **kwargs)
        self.rect = super().give_rect()

    def __copy__(self):
        new_instance = Domino(list(self.vals))
        new_instance.placed = self.placed
        new_instance.empty = self.empty
        new_instance.extra = self.extra
        new_instance.jump = self.jump
        new_instance.acotao = self.acotao
        new_instance.in_screen = self.in_screen
        new_instance.path = self.path
        new_instance.rect = self.rect.copy()

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

    def show(self):
        self.in_screen = True
        super().show()

    def hide(self):
        self.in_screen = False
        super().hide()

    def update(self):
        x, y = super().give_position()
        if super().is_colliding(pygame.mouse.get_pos()) and self.placed == False and self.in_screen == True:
            if self.empty:
                self.placed = True
                self.jump = False

            if self.jump:
                self.on_hover()
        
        else:
            # print("UPDATE")
            super().update()
            self.jump = True
        # print("UPDATE")
        self.x, self.y = x, y

    def extra_dominoes_is_empty(self):
        self.empty = True

    def on_hover(self):
        pixels_to_move = 2
        self.y -= pixels_to_move

        new_height = self.rect.height + pixels_to_move*2
        self.rect.height = new_height
        self.rect.center = (self.x, self.y)
        self.jump = False

    def sum_vals(self):
        return int(self.vals[0]) + int(self.vals[1])

    def click_me(self):
        if self.in_screen:
            mouse_position = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_position):
                print("domino originalobjects.py clicked!")
                return True
            else:
                print("domino originalobjects.py not clicked!")
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

        super().__init__(img_path=os.path.join("assets", "Dominos (Interface)", self.path1), x_scale=1, y_scale=1, orientation=0)
        self.rect = super().give_rect()

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
        if self.in_screen:
            if super().is_colliding(pygame.mouse.get_pos()):
                super().change_sprite(os.path.join("assets", "Dominos (Interface)", self.path2))

            else:
                super().change_sprite(os.path.join("assets", "Dominos (Interface)", self.path1))  
            
        super().update()

    def click_me(self):
        if self.in_screen:
            mouse_position = pygame.mouse.get_pos()
            print(f"mouse_position: {mouse_position}")
            if self.rect.collidepoint(mouse_position):
                print("button originalobjects.py clicked!")
                return True
            else:
                print("button originalobjects.py not clicked!")
                return False


class Player:
    def __init__(self, num, manual=True):
        self.dominoes = np.array([])
        self.first_pick = True
        self.manual = manual
        self.points = 0
        self.num = num

    def add_domino(self, domino):
        # print(f"domino onjects 254: {domino}")
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