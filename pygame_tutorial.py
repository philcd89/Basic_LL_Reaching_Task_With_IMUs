# -*- coding: utf-8 -*-
"""
Created on Thu Feb  4 14:28:28 2021

@author: philc
"""
import sys
import pygame
from win32api import GetSystemMetrics as SysMet

#%% Initialize game
pygame.init()

#initialize game screen
width = SysMet(0)
height = round(SysMet(1)*0.92) # 95-ish% of screen height, to allow for window bar to be seen
screen = pygame.display.set_mode((width, height))

#%% Window title
pygame.display.set_caption("Basic Reaching Task")
# icon = pygame.image.load("imagename.png")
# pygame.display.set_icon(icon)

#%% Set target parameters

# Home Position Parameters
HomeX = round(width/2)
HomeY = round(height*0.75) # 3/4 down screen from bottom
HomeRad = 20

# Target Parameters
TargX = round(width/2)
TargY = HomeY - 400
TargRad = 20

# Cursor Parameters
CursX = round(width/2)
CursY = HomeY - 400
CursRad = 12

def HomePos():
    pygame.draw.circle(screen, (255, 0, 0), (HomeX, HomeY), HomeRad)
    
def TargPos():
    pygame.draw.circle(screen, (255, 0, 0), (TargX, TargY), TargRad)

def CursPos():
    pygame.draw.circle(screen, (255, 255, 255), (CursX, CursY), CursRad)    

#%% Main game loop
run = True
try:
    while run == True:
        
        # persistent parameters should stay in while loop
        
        pygame.mouse.set_visible(False)
        
        screen.fill((0,0,0)) # black
        HomePos()
        TargPos()
        
        CursX = pygame.mouse.get_pos()[0]
        CursY = pygame.mouse.get_pos()[1]
        CursPos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
        pygame.display.update()
        
except KeyboardInterrupt:
    sys.exit("User quit game")