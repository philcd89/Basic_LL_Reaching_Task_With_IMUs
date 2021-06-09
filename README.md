# Lower Limb Obstacle Avoidance Task With IMUs

This is a lower limb reaching task in which participants make lower limb movements (e.g., knee flexion/extension) while Inertial Measurement Units (IMUs) control a cursor on a screen and move it between two points.  Obstacles sometimes appear, and the participant is asked to avoid the obstacle.  This code uses [MotionNode](https://www.motionnode.com/) sensors and borrows heavily from their SDK.  Note: This task was my first time using Python, so don't judge my janky code too much.

**PURPOSE:** The purpose of this task is to investigate how participants are able to make adjustments to online movements of their lower limbs.

<br>

## Files in this repository

* *README.md*: You're looking at it!  This file provides info about the task, the files in this repository, 
* *LL_obstacle_avoidance_task_IMU.py*: This is the main file that runs the task
* *MotionSDK.py*: This file is made by MotionNode and supplies functions used to read data from the IMUs
* *Calibration.py*: This file is used to account variation in the placement of the IMU on the participants leg, and also to account for the participant's subjective "straight ahead" knee flexion/extension.
* *trial_conditions_example.txt*: This text file contains the condition numbers for each trial run in a PRACTICE block.  Any block calling this text file will run the number of trials equivalent to lines in this file (i.e., this file determines the number of trials in a block, as well as the condition type of each trial).
* *trial_conditions.txt*: This text file contains the condition numbers for each trial run in an EXPERIMENTAL block.  Any block calling this text file will run the number of trials equivalent to lines in this file (i.e., this file determines the number of trials in a block, as well as the condition type of each trial).
* *LICENSE*: This file provides a Creative Commons License for this project

<br>

## Understanding Trial Conditions

There are 5 trial types (i.e., conditions) in this task:
1) No Obstacle (Condition 0)
2) Obstacle appears prior to cue (Condition 1)
3) Obstacle appears with cue (Condition 2)
4) Obstacle appears with movement onset (Condition 3)
5) Obstacle appears at 20% of movement amplitude (Condition 4)

This purpose of this condition design is to probe how the motor system is able to alter online movements when new information is supplied at different stages in the motor planning/execution process.

In the *trial_conditions.txt* and *trial_conditions_example* files the condition of each trial is denoted by the condition number on each line, one line per trial.

<br>

## Prerequisite software

This task is run via python.  The best way to download python is to get the most current [Anaconda](https://www.anaconda.com/products/individual) release.

This task also uses Pygame, a python module used to design and run simple computer games.  To download pygame:
1) Open anaconda prompt
2) type *pip install pygame*, and hit Enter.

<br>

## Downloading this task from GitHub

This task needs to be downloaded from github to use.  You can download it as a zipped folder, or [clone](https://docs.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository-from-github/cloning-a-repository) this repository to your computer.  While the task can also be stored on the lab drive, DO NOT run the task from the drive - run the task from a local location.  If you run the task from the lab drive, the task will lag because the task needs to read/write over an internet connection.


## Applying the IMUs

MotionNode IMUs need to be applied to the participant in a specific way for this task:

1) Place velcro straps on participant thighs and shanks.  Longer straps are for the thighs, shorter straps for the shanks.  Straps should be tight, but not overly so.  Thigh straps should be placed approximately 1/2 way between the lateral epicondyle of the femur (outer knee) and great trochanter of femur (outer hip).  Shank straps should placed approximately 1/2 way between the lateral epicondyle of the femur and the lateral malleolus of ankle.  Make sure that the velcro part of the strap is not on the outside of the leg, as that is where the IMU will be placed.  **TIP:** It is best if participants are asked to wear shorts or athletic clothes for the experiment. 
     
     <img src="https://user-images.githubusercontent.com/48997660/121388792-c5831680-c919-11eb-84fd-ba450e054f99.JPG" width="150" height="200">

2) Don the IMU belt, positioning the waist IMU in the center of the back, at approximately the L4 vertebra.  
3) **WARNING: THIS STEP IS CRITICAL.** The IMUs are labeled according to their segments.  They should be placed on the **OUTSIDE** of the leg on their respective segments, **WIRES UP**.  This is particularly important for the shank IMUs, which are the IMUs drive the task.  Do your best to place the IMUs such that they'll move in the sagittal plane. Note: I like to wiggle the IMUs into the velcro to make sure the velcro digs in well.  You can also wrap the IMUs in athletic prewrap to keep them secure.  Wire slack can be taken in with clips.

     <img src="https://user-images.githubusercontent.com/48997660/121392287-3d9f0b80-c91d-11eb-8a10-8208068bfb63.JPG" width="150" height="200">

<br>

## Connecting to MotionNode

1) On the IMU system, plug in the battery via the USB cord that comes off the central rectangular unit.
2) When the small white light on the central unit shows solid white, connect via wifi to "Bus" on the computer you will use.
3) Open MotionNode software
4) Click "Devices"
5) Click "Scan for Devices"
6) When "Bus" appears, click "Bus".  MotionNode should now be connected to the IMU system.
7) Click "Help".  Click "Calibrate".  With IMUs motionless, click "Start".  Wait until the calibration is complete.
8) Click "Node Viewer".  Hover over the "+" button in the bottom right of the screen.  Hit the ">" button to connect to the IMUs.  Select a node (an IMU). The animation should now follow the motion of the IMU.

<br>

## Running the task

1) Open Anaconda Powershell Prompt.  This should be located with the Ananconda installation in the Start Menu or Apps menu, or you can search this on the computer and it should come right up.
2) Change the directory to the place where *LL_obstacle_avoidance_task_IMU.py* is stored on the computer.  For Laptop Z, these should be in a folder called *LL_obstacle_avoidance_task_IMU-main* which itself is in the *Documents* folder.  To change the directory, use the "cd" command, followed by the directory of the folder in quotes.  For example:

     cd "C:\Users\philc\Documents\LL_obstacle_avoidance_task_IMU-main"
     
3) To run the task, type the following:

     LL_obstacle_avoidance_task_IMU.py --header --datafile="mydatafile.txt" --trialfile="mytrialfile.txt"
     
     The text "mydatafile.txt" and "mytrialfile.txt" are where the data are saved.  These can be replaced by another valid filename (i.e., subject number, etc.).  More on output below.
     

