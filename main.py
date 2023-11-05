import PySimpleGUI as sg
import random
import time
import sys
import heapq
from collections import deque

GRID_SIZE = 50 
BOT = 1

SHIP = [GRID_SIZE][GRID_SIZE]

def rand(n):
    return random.randint(0,n-1)

blocked_cells = []
dead_ends = {}

first_cell_x = rand(GRID_SIZE)
first_cell_y = rand(GRID_SIZE)
corridor_dict = {(first_cell_x, first_cell_y): True}

def within_bounds(pair):
    i = pair[0]
    j = pair[1]
    return i >= 0 and i < GRID_SIZE and j >= 0 and j < GRID_SIZE

def dead_end(pair):
    i = pair[0]
    j = pair[1]
    cnt = 0
    if ((i+1),j) in corridor_dict: cnt += 1
    if ((i-1),j) in corridor_dict: cnt += 1
    if (i,(j+1)) in corridor_dict: cnt += 1
    if (i,(j-1)) in corridor_dict: cnt += 1
    return cnt == 1

def is_blocked(pair):
    i = pair[0]
    j = pair[1]
    if (i,j) in corridor_dict: return False
    cnt = 0
    if (i+1,j) in corridor_dict: cnt += 1
    if (i-1,j) in corridor_dict: cnt += 1
    if (i,j+1) in corridor_dict: cnt += 1
    if (i,j-1) in corridor_dict: cnt += 1
    return cnt == 1

def add_cells_initialization(pair):
    i = pair[0]
    j = pair[1]
    if within_bounds((i-1,j)) and is_blocked((i-1, j)): 
        blocked_cells.append((i-1,j))
    if within_bounds((i+1,j)) and is_blocked((i+1,j)): 
        blocked_cells.append((i+1, j))
    if within_bounds((i,j-1)) and is_blocked((i,j-1)): 
        blocked_cells.append((i, j-1))
    if within_bounds((i,j+1)) and is_blocked((i,j+1)): 
        blocked_cells.append((i, j+1))

add_cells_initialization((first_cell_x, first_cell_y))

# returns random pair that is in corridor
def randValid():
    while True:
        loc = (rand(GRID_SIZE),rand(GRID_SIZE))
        if loc in corridor_dict: return loc

# opens closed neighbors in random order
def open_closed_neighbor(pair):
    list = [(-1,0),(1,0),(0,-1),(0,1)]
    random.shuffle(list)
    for pair_2 in list:
        possible_pair = ((pair[0] + pair_2[0]), (pair[1]+pair_2[1]))
        if within_bounds(possible_pair) and possible_pair not in corridor_dict:
            to_be_added[possible_pair] = True
            break


while(len(blocked_cells) != 0):
    rand_index = rand(len(blocked_cells))
    if is_blocked(blocked_cells[rand_index]):
        corridor_dict[blocked_cells[rand_index]] = True
        add_cells_initialization(blocked_cells[rand_index])
    blocked_cells.pop(rand_index)

# opens half dead ends
to_be_added = {}
for pair,_ in corridor_dict.items():
    if dead_end(pair) == True and rand(2) == 1:
        open_closed_neighbor(pair)
        
for pair,_ in to_be_added.items():
    corridor_dict[pair] = True

# initializes locations of robot and end location
robot_location = randValid()
robot_path = {} # all cells that robot plans on traversing through
goal_location = randValid()