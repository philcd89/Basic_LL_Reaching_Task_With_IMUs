# -*- coding: utf-8 -*-
"""
Created on Tue Apr 20 12:23:52 2021

@author: philc

This cose will calibrate the LL obstacle reaching task such that 
"""
#%% Setup
import sys
import pygame
import math as m
import numpy as np
import pandas as pd

from win32api import GetSystemMetrics as SysMet
from xml.etree.ElementTree import XML
from scipy.signal import find_peaks
from scipy.signal import argrelextrema
from scipy.spatial.transform import Rotation as R
from matplotlib import pyplot as plt

import MotionSDK

#%% Get name map
def parse_name_map(xml_node_list):
    name_map = {}

    tree = XML(xml_node_list)

    # <node key="N" id="Name"> ... </node>
    list = tree.findall(".//node")
    for itr in list:
        name_map[int(itr.get("key"))] = itr.get("id")

    return name_map


def calib_instructions():
    pygame.init()
    pygame.display.set_caption("Basic Reaching Task")
    font = pygame.font.SysFont("Arial", 28)
    width = SysMet(0)
    height = round(SysMet(1)*0.92) # 95-ish% of screen height, to allow for window bar to be seen
    screen = pygame.display.set_mode((width, height))
    
    run = True
    finished_Instructions = False
    while run:
        screen.fill((0,0,0))
        
        text = font.render("Calibration Block", True, (255, 255, 255))
        screen.blit(text, (width/2 - text.get_rect().width/2, (height/2)-50))
     
        text = font.render("After finishing these instructions, please peform continuous lower limb flexion/extension movements", True, (255, 255, 255))
        screen.blit(text, (width/2 - text.get_rect().width/2, (height/2)+50))
        
        text = font.render("until prompted to stop (~10 seconds).", True, (255, 255, 255))
        screen.blit(text, (width/2 - text.get_rect().width/2, (height/2)+80))
        
        text = font.render("Press SPACEBAR to continue and begin flextion/extension movements...", True, (255, 255, 255))
        screen.blit(text, (width/2 - text.get_rect().width/2, (height/2)+140))
        
        pygame.display.update()
        
        # --------- GET EVENTS ---------- 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit("User quit game")
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    finished_Instructions = True
        
        if finished_Instructions:
            screen.fill((0,0,0))
            pygame.display.update() 
            run = False 
    
    return screen


#%% Define Calibration Function
def Calibration(screen, host = "127.0.0.1", port = 32076, samples = 1000, header = True):
    
    #Initialize Client
    client = MotionSDK.Client(host, port)
    
    xml_string = \
        "<?xml version=\"1.0\"?>" \
        "<configurable inactive=\"1\">" \
        "<g/>" \
        "<r/>" \
        "</configurable>"

    if not client.writeData(xml_string):
        raise RuntimeError(
            "failed to send channel list request to Configurable service")
    
    sample = 0
    run = True
    
    font = pygame.font.SysFont("Arial", 28)
    width = SysMet(0)
    height = round(SysMet(1)*0.92) # 95-ish% of screen height, to allow for window bar to be seen
    
    while run:
        
        ########### DISPLAY CALIBRATION INSTRUCTIONS ###########
        pygame.mouse.set_visible(False)
        screen.fill((0, 0, 0))
        current_time = pygame.time.get_ticks()
        
        
        text = font.render("perform continuous lower limb flexion/extension movements", True, (255,255,255))
        screen.blit(text, (width/2 - text.get_rect().width/2, (height/2)+50))
        
        pygame.display.update()
        
        ################# STREAM IMU DATA ################
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
            if header:
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
                headerOut = "sampleNum," + headerOut
                

            xml_node_list = None

            
            
        ########### FILL DATAFRAME ############
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
            
        



        ########### CREATE and/or APPEND DATA ON DATAFRAME ###########
        sample += 1 
        
        try:
            calib_data
        except NameError:
            calib_data = pd.DataFrame(columns = headerOut.split(','))
        flat_list.insert(0,sample)    
        calib_data.loc[sample-1] = np.asarray(flat_list)
        
    
        if sample >= samples:
            run = False
            
    screen.fill((0,0,0))
    text = font.render("Calibration Complete.  Hold leg in neutral position", True, (255,255,255))
    screen.blit(text, (width/2 - text.get_rect().width/2, (height/2)+50))
    pygame.display.update()
    pygame.time.wait(4000)
    return calib_data
    
#%% Define funtion to generate calibrated theta
def Compute_Calib_Theta():
    screen = calib_instructions()
    calib_data = Calibration(screen)
    
    # calib_data = pd.read_csv("calib_data.csv")
    # calib_data = calib_data.drop(calib_data.columns[0], axis = 1)
    
    # Use raw gyroscope readings (degrees/sec)
    # FOR IMU PLACED ON SIDE OF SHANK: 
    # X controlled by z gyroscope
    # Y controlled by y gyroscope
    gx = np.asarray(calib_data.loc[:,"Node03.gz"])
    gy = np.asarray(calib_data.loc[:,"Node03.gy"])
    
    velT = np.sqrt(gx**2 + gy**2)   # Compute tangential velocity
    # velT_mean = velT.mean() # find mean tangential velocity
    
    ind_velT_max = argrelextrema(velT, np.greater)[0] # Find local maxima (should roughly correspond to central leg position)
    ind_velT_min = argrelextrema(velT, np.less)[0] # Find local minima (should correspond to points of maximum flexion and extension)
    
    # Find only those indices where theres a minimum 25 sample gap in between consecutive mins/maxes
    ind_velT_max_clean = []
    ind_velT_min_clean = []
    for i, val in enumerate(ind_velT_max):
        if i == 0:
            pass
        elif val - ind_velT_max[i-1] > 25:
            ind_velT_max_clean.append(val)
    for i, val in enumerate(ind_velT_min):
        if i == 0:
            pass
        elif val - ind_velT_min[i-1] > 25:
            ind_velT_min_clean.append(val)
    ind_velT_max_clean = np.asarray(ind_velT_max_clean)
    ind_velT_min_clean = np.asarray(ind_velT_min_clean)
        
    
    posx = gx.cumsum()
    posy = gy.cumsum()
    
    # Find mean location of max velocity (should be roughly the home position)
    velMaxPos_xMean = posx[ind_velT_max_clean].mean()
    velMaxPos_yMean = posy[ind_velT_max_clean].mean()
    
    # Find which velMins are associated with extension using y coordinate
    velMinPos_y = posy[ind_velT_min_clean]
    velMinPost_indExt = np.where(velMinPos_y > velMaxPos_yMean)
    velMinPost_indFlex = np.where(velMinPos_y < velMaxPos_yMean)
    
    # Find mean x and y position of flexion and extension clusters
    velMin_extPos_xMean = posx[ind_velT_min_clean[velMinPost_indExt]].mean()
    velMin_extPos_yMean = posy[ind_velT_min_clean[velMinPost_indExt]].mean()
    velMin_flexPos_xMean = posx[ind_velT_min_clean[velMinPost_indFlex]].mean()
    velMin_flexPos_yMean = posy[ind_velT_min_clean[velMinPost_indFlex]].mean()
    
    # Find x and y displacement between flexion and extension
    xdiff = velMin_flexPos_xMean - velMin_extPos_xMean
    ydiff = velMin_flexPos_yMean - velMin_extPos_yMean
    
    # Find theta in radians
    # theta = 0
    theta = m.atan(xdiff/ydiff)
    
    # Visualize peaks and clusters
    # plt.plot(velT)
    # plt.plot(ind_velT_max_clean, velT[ind_velT_max_clean], "x")
    # plt.plot(ind_velT_min_clean, velT[ind_velT_min_clean], "x")
    # plt.show()
    
    # fig, ax = plt.subplots(1)
    # plt.plot(posx, posy)
    # plt.plot(posx[ind_velT_max_clean], posy[ind_velT_max_clean], "x")
    # plt.plot(posx[ind_velT_min_clean], posy[ind_velT_min_clean], "x")
    # plt.plot(velMaxPos_xMean, velMaxPos_yMean, "x")
    # plt.plot(velMin_extPos_xMean, velMin_extPos_yMean, "x")
    # plt.plot(velMin_flexPos_xMean, velMin_flexPos_yMean, "x")
    # ax.set_aspect("equal", adjustable = "datalim")
    # plt.show()    
    
    
       
    return [screen, theta]
    
    

    
    
#%% Define Main to run as script

def main():
    screen, theta = Compute_Calib_Theta()
    return [screen, theta]

    
        
#%% RUN THIS THANNGGGG
if __name__ == "__main__":
    screen, theta = main()















