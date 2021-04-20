# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 14:01:07 2021
@author: philc
This code is a first attempt at piping MotionNode data from the path into a txt file, while also driving the task
"""

#%% Setup

import argparse
import sys
import pygame
import math as m
import numpy as np

from win32api import GetSystemMetrics as SysMet

from xml.etree.ElementTree import XML

from scipy.spatial.transform import Rotation as R

import MotionSDK

#%% Get trial Conditions

# Get trial conditions
condfile = open("trial_conditions.txt", "r")
trial_conditions = np.asarray(list(map(int, condfile.readlines())))

#%% Initialize Screen and Set target parameters

#initialize colors
black = (0,0,0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 255)

#initialize game screen
width = SysMet(0)
height = round(SysMet(1)*0.92) # 95-ish% of screen height, to allow for window bar to be seen
screen = pygame.display.set_mode((width, height))

# Set constants
centerX = round(width/2)
centerY = round(height/2)
HomeX = round(width/2)
HomeY = round(height*0.75) # 3/4 down screen from bottom
HomeRad = 20
TargX = round(width/2)
TargY = round(height*0.75) - 400
TargRad = 20
CursRad = 12
ObstY = round(height*0.75) - 300
ObstLength = 10
ObstWidth = 150
CounterX = 20
CounterY = 20

pygame.init()
pygame.display.set_caption("Basic Reaching Task")
# icon = pygame.image.load("imagename.png")
# pygame.display.set_icon(icon)
clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 28)

#%% Define object parameters

def Blank_Screen(color):
    screen.fill(color)  
    
def Instructions(x = centerX, y = centerY):
    
    font = pygame.font.SysFont("Arial", 28)
    
    text = font.render("Instructions", True, white)
    screen.blit(text, (x - text.get_rect().width/2, y-50))
 
    text = font.render("...some instructions could go here....", True, white)
    screen.blit(text, (x - text.get_rect().width/2, y+50))
    
    text = font.render("press space to continue", True, white)
    screen.blit(text, (x - text.get_rect().width/2, y+100))
    
    pygame.display.update()

def HomePos(HomeX, HomeY, HomeRad, color):
    # Home Position Parameters
    pygame.draw.circle(screen, color, (HomeX, HomeY), HomeRad)
    
def TargPos(TargX, TargY, TargRad, color):
    # Target Parameters
    pygame.draw.circle(screen, color, (TargX, TargY), TargRad)

def CursPos(x, y, CursRad, color):
    # Cursor Parameters
    pygame.draw.circle(screen, color, (x, y), CursRad)    
    
def Obstacle(color = red, Length = ObstLength, Width = ObstWidth, x = centerX, y = ObstY):
    # Obstacle Parameters
    rect_left = x - (Width/2)
    rect_top = y
    rect_width = Width
    rect_length = Length
    RectParams = (rect_left, rect_top, rect_width, rect_length)
    pygame.draw.rect(screen, color, rect = RectParams)  
    
def Obst_Counter(x, y, font, obstacles_hit):
    
    text = font.render("Obstacles Hit: " + str(obstacles_hit), True, white)
    screen.blit(text, (x, y))
    

#%% INSTRUCTIONS
run = True
finished_Instructions = False

#Instructions
while run:
    
    # persistent parameters should stay in while loop
        
    # --------- GET EVENTS ---------- 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit("User quit game")
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                finished_Instructions = True
    
    
    # --------- INSTRUCTIONS -----------
    
    # first, show some instructions
    Instructions()
        
    if finished_Instructions:
        Blank_Screen(black)
        pygame.display.update() 
        pygame.time.wait(2000)
        run = False
    
  
#%% IMU Control

def parse_name_map(xml_node_list):
    name_map = {}

    tree = XML(xml_node_list)

    # <node key="N" id="Name"> ... </node>
    list = tree.findall(".//node")
    for itr in list:
        name_map[int(itr.get("key"))] = itr.get("id")

    return name_map

def stream_data_to_csv(args, out):
    client = MotionSDK.Client(args.host, args.port)

    #
    # Request the channels that we want from every connected device. The full
    # list is available here:
    #
    #   https://www.motionshadow.com/download/media/configurable.xml
    #
    # Select the local quaternion (Lq) and positional constraint (c)
    # channels here. 8 numbers per device per frame. Ask for inactive nodes
    # which are not necessarily attached to a sensor but are animated as part
    # of the Shadow skeleton.
    #
    
    # ADDING linear acceleration (la) and euler angle (r) set!!!!  This should add 6 more numbers per device per frame.
    xml_string = \
        "<?xml version=\"1.0\"?>" \
        "<configurable inactive=\"1\">" \
        "<g/>" \
        "<r/>" \
        "</configurable>"

    if not client.writeData(xml_string):
        raise RuntimeError(
            "failed to send channel list request to Configurable service")

    num_frames = 0
    sample = 1
    xml_node_list = None   
    
    # ------------ SET PYGAME CONSTANTS AND INITIAL STATES --------------
    
    # Pygame stuff
    main_loop_start_time = pygame.time.get_ticks()
    
    # Cursor Control
    xGain = 0.1
    yGain = 0.1
    
    # Colors
    homeColor = red
    targColor = red
    
    # Trials and Samples
    sample = 1
    trial = 0
    
    #Timing
    curs_in_targ_time = 0
    move_start_time = 0
    wait_in_home = 3000
    hold_in_targ = 300
    wait_in_targ = 2000
    show_obst_pre_move = 1000
    curs_in_home_time = 0
    curs_in_obst_time = 0
    
    # Initial States
    curs_in_home = False
    curs_in_targ = False
    targ_hit = False
    curs_in_home_prev = False
    curs_in_targ_prev = False
    targ_hit_prev = False
    move_back_prev = False
    move_back = True
    move_out = False
    show_obstacle = False
    cue_on = False
    trial_cond = 0
    curs_in_obst = False
    curs_in_obst_prev = False
    obst_hit_counter = 0
    fill_color = black
    
    curs_in_obst_xmin = centerX - (ObstWidth/2) - CursRad   
    curs_in_obst_xmax = centerX + (ObstWidth/2) + CursRad
    curs_in_obst_ymin = ObstY - CursRad                     # This is all weird because the rect is placed based on the top right
    curs_in_obst_ymax = ObstY + ObstLength + CursRad
    
    while True:
        
        # Block, waiting for the next sample.
        data = client.readData()
        if data is None:
            raise RuntimeError("data stream interrupted or timed out")
            break

        if data.startswith(b"<?xml"):
            xml_node_list = data
            continue

        container = MotionSDK.Format.Configurable(data)

        #
        # Consume the XML node name list. If the print header option is active
        # add that now.
        #
        if xml_node_list:
            if args.header:
                ChannelName = [
                    "gx", "gy", "gz",
                    "rx", "ry", "rz"
                ]

                name_map = parse_name_map(xml_node_list)

                flat_list = []
                for key in container:
                    if key not in name_map:
                        raise RuntimeError(
                            "device missing from name map, unable to print "
                            "header")

                    item = container[key]
                    if len(ChannelName) != item.size():
                        raise RuntimeError(
                            "expected {} channels but found {}, unable to "
                            "print header".format(
                                len(ChannelName), item.size()))

                    name = name_map[key]
                    for channel in ChannelName:
                        flat_list.append("{}.{}".format(name, channel))

                if not len(flat_list):
                    raise RuntimeError(
                        "unknown data format, unabled to print header")

                headerOut = ",".join(["{}".format(v) for v in flat_list])
                headerOut = "sampleNum," + headerOut + "," + "CursorX," + "CursorY" + "\n"
                out.write(headerOut)
                
                # out.write(
                #     ",".join(["{}".format(v) for v in flat_list]))

            xml_node_list = None

        #
        # Make an array of all of the values, in order, that are part of one
        # sample. This is a single row in the output.
        #
        flat_list = []
        for key in container:
            item = container[key]
            for i in range(item.size()):
                flat_list.append(item.value(i))

        if not len(flat_list):
            raise RuntimeError("unknown data format in stream")

        # ###################### PYGAME CODE ######################
        
        
        # Get some constants for this loop
        pygame.mouse.set_visible(False)
        screen.fill(fill_color)
        current_time = pygame.time.get_ticks()
        
        
        
        
        
        # ---------- SET PRIORS ----------
        
        # Set prior states
        curs_in_home_prev = curs_in_home
        curs_in_targ_prev = curs_in_targ
        targ_hit_prev = targ_hit
        move_back_prev = move_back
        curs_in_obst_prev = curs_in_obst
            
        
        
        
        
        # ------------ CURSOR CONTROL ----------------

        # Use raw gyroscope readings (degrees/sec)
        # FOR IMU PLACED ON SIDE OF SHANK: 
        # X controlled by z gyroscope (flat_list[20])
        # Y controlled by y gyroscope (flat_list[19])
            
        if(sample == 1):
            CursX = HomeX
            CursY = HomeY
        else:
            CursX -= flat_list[20]*xGain
            CursY -= flat_list[19]*yGain
        
        # Determine distances
        dist_to_home = m.sqrt((abs(CursX-HomeX)**2) + (abs(CursY-HomeY)**2))
        dist_to_targ = m.sqrt((abs(CursX-TargX)**2) + (abs(CursY-TargY)**2))
        
        
        
        
        
        # --------- IS THE CURSOR IN THE TARGET(S)? ---------
        if dist_to_home < (CursRad + HomeRad):
            curs_in_home = True
        else:
            curs_in_home = False
            
        if dist_to_targ < (CursRad + TargRad):
            curs_in_targ = True
        else:
            curs_in_targ = False
            
            
            
            
            
        # --------- LOOK FOR STATE CHANGES, GET TIME, AND CREATE EVENT ---------
        if curs_in_home and not curs_in_home_prev:
            curs_in_home_time = pygame.time.get_ticks()
            
        if not curs_in_home and curs_in_home_prev:
            move_start_time = pygame.time.get_ticks()
            
        if curs_in_targ and not curs_in_targ_prev:
            curs_in_targ_time = pygame.time.get_ticks()
            
            
        
        # ----------- MANAGE EVENTS -------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit("User quit game")
        
        
        
        
        # ----------- MAIN TRIAL LOOP ------------
        
        # Participant waits in home position, after period of time, target turns green to cue movement
        if curs_in_home and (current_time - curs_in_home_time > wait_in_home):
            cue_on = True
            targColor = green
            
        
        # Determine if the participant has begun to reach
        if not move_back and not curs_in_home and not curs_in_targ and cue_on:
            move_out = True
            
        # Participant must briefly hold in target, and signal move_out is over
        if curs_in_targ and (current_time - curs_in_targ_time > hold_in_targ):
            #play a sound?
            targ_hit = True
            move_out = False
            move_back = True
            
        # After target is hit, wait a period of time before turning target back to red
        if targ_hit and (current_time - curs_in_targ_time > wait_in_targ):
            targColor = red
            cue_on = False
                    
        # Once participant leaves target, turn targ_hit to False
        if not move_out and move_back and not curs_in_home and not curs_in_targ:
            targ_hit = False
            
        # If participant is once again in home position, change move_back to False
        if curs_in_home and move_back:
            move_back = False
        
        if not move_back and move_back_prev: #if move_back switches from true to false, signalling the end of the trial, advance the trial number
            trial += 1
            curs_in_obst = False
            
        # ---------- SET TRIAL CONDITION -----------
        
        trial_cond = trial_conditions[trial-1]
        
        
        
        # ---------- MANAGE OBSTACLE PRESENTATION ----------
        
        # No obstacle
        if trial_cond == 0:
            show_obstacle = False
        
        # Present obstacle prior to movement cue
        elif trial_cond == 1:
            if curs_in_home and (current_time - curs_in_home_time > show_obst_pre_move):
                show_obstacle = True
            elif targ_hit and (current_time - curs_in_targ_time > wait_in_targ):
                show_obstacle = False
       
        # Present obstacle with movement cue
        elif trial_cond == 2:
            if curs_in_home and (current_time - curs_in_home_time > wait_in_home):
                show_obstacle = True
            elif targ_hit and (current_time - curs_in_targ_time > wait_in_targ):
                show_obstacle = False
        
        # Present obstacle with movement onset
        elif trial_cond == 3:
            if move_out and not move_back and (current_time - curs_in_home_time > wait_in_home):
                show_obstacle = True
            elif targ_hit and (current_time - curs_in_targ_time > wait_in_targ):
                show_obstacle = False
                
        # Present obstacle when cursor is 1/3 of the way through the movement
        elif trial_cond == 4:
            if move_out and not move_back and CursY < (HomeY - (round((HomeY - TargY)/3))):
                show_obstacle = True
            elif targ_hit and (current_time - curs_in_targ_time > wait_in_targ):
                show_obstacle = False    
                
                
                
        # --------- MANAGE OBSTACLE COLLISION ----------
        
        if show_obstacle and curs_in_obst_xmin < CursX < curs_in_obst_xmax and curs_in_obst_ymin < CursY < curs_in_obst_ymax:
            curs_in_obst = True
            
        # Check for state change in obstacle
        if curs_in_obst and not curs_in_obst_prev:
            curs_in_obst_time = pygame.time.get_ticks()
            obst_hit_counter += 1
            
        if current_time - curs_in_obst_time < 100: #flash screen 50 milliseconds
            fill_color = red
        else:
            fill_color = black
                
        
        
        

        # --------- UPDATE DISPLAY ----------    
        
        HomePos(HomeX, HomeY, HomeRad, homeColor)
        TargPos(TargX, TargY, TargRad, targColor)
        if show_obstacle:
            Obstacle()
        CursPos(CursX, CursY, CursRad, white)
        Obst_Counter(CounterX, CounterY, font, obst_hit_counter)
        
        pygame.display.update()
        
        # ------------ SCOPE ------------
        print(clock.get_fps())
        
                
        # ------------ SAVE DATA --------------
        
        dataOut = ",".join(["{}".format(round(v, 8)) for v in flat_list])
        dataOut = str(sample) + "," + dataOut + "," + str(CursX) + "," + str(CursY) + "\n"
        
        #out.write(dataOut)

        sample += 1

        if args.frames > 0:
            num_frames += 1
            if num_frames >= args.frames:
                break

#%% Define input args
            
def main(argv):
    parser = argparse.ArgumentParser(
        description="")

    parser.add_argument(
        "--file",
        help="output file",
        default="")
    parser.add_argument(
        "--frames",
        help="read N frames",
        type=int, default=0)
    parser.add_argument(
        "--header",
        help="show channel names in the first row",
        action="store_true")
    parser.add_argument(
        "--host",
        help="IP address of the Motion Service",
        default="127.0.0.1")
    parser.add_argument(
        "--port",
        help="port number address of the Motion Service",
        type=int, default=32076)

    args = parser.parse_args()

    if args.file:
        with open(args.file, 'w') as f:
            stream_data_to_csv(args, f)
    else:
        stream_data_to_csv(args, sys.stdout)
        
#%% RUN THIS THANNGGGG
if __name__ == "__main__":
    sys.exit(main(sys.argv))
