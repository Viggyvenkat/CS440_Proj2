import random
import time
import sys
import heapq
from collections import deque
import pandas 
import math 

def rand(n):
    return random.randint(0,n-1)

GRID_SIZE = 50 
blocked_cells = []
dead_ends = {}
#SHIP = [GRID_SIZE][GRID_SIZE]
BOT = 1

first_cell_x = rand(GRID_SIZE)
first_cell_y = rand(GRID_SIZE)
    
blocked_cells = []
dead_ends = {}

corridor_dict = {
    (first_cell_x, first_cell_y): True
}

def rand(n):
    return random.randint(0,n-1)

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

def within_bounds(pair):
    i = pair[0]
    j = pair[1]
    return i >= 0 and i < GRID_SIZE and j >= 0 and j < GRID_SIZE

def open_closed_neighbor(to_be_added,pair):
    list = [(-1,0),(1,0),(0,-1),(0,1)]
    random.shuffle(list)
    for pair_2 in list:
        possible_pair = ((pair[0] + pair_2[0]), (pair[1]+pair_2[1]))
        if within_bounds(possible_pair) and possible_pair not in corridor_dict:
            to_be_added[possible_pair] = True
            break

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

# initializes cells
add_cells_initialization((first_cell_x, first_cell_y))

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
        open_closed_neighbor(corridor_dict, pair)
        
for pair,_ in to_be_added.items():
    corridor_dict[pair] = True

def randValid():
    while True:
        loc = (rand(GRID_SIZE),rand(GRID_SIZE))
        if loc in corridor_dict: return loc

def leakRandValid(pair):
    while True:
        loc = (rand(GRID_SIZE),rand(GRID_SIZE))
        if loc in corridor_dict: 
            if loc[0] < 2 * pair[0] + 1 or loc[1] < 2 * pair[1] + 1:
                return leakRandValid(pair)
            else:
                return loc

print(corridor_dict)

def detect(bot, leak):
    if(leak[0] < 2 * bot[0] + 1 or leak[1] < 2 * bot[1] + 1):
        return True 
    return False

def create_detection_square(bot):
    lst = []
    for i in range(1, 2):
        for j in range(1, 2):
            lst.append((i * bot[0]), (j * bot[1]))
    return lst         


def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3

def next_move(bot, MAY_CONTAIN_LEAK):
    minimum_distance = math.dist(MAY_CONTAIN_LEAK[0], bot)
    min_coords = MAY_CONTAIN_LEAK[0]
    for (i,j) in MAY_CONTAIN_LEAK[1:]:
        if (math.dist((i,j), bot) < minimum_distance):
            minimum_distance = math.dist((i,j), bot)
            min_coords = (i,j)
    return min_coords

def deterministic_search():
    bot = randValid()
    leak = leakRandValid()
    MAY_CONTAIN_LEAK = []

    for i,j in corridor_dict:
        if (i,j) == bot:
            continue
        MAY_CONTAIN_LEAK.append((i,j))
    
    actions = 0
    if BOT == 1:
        while bot != leak: 
            if(detect(bot, leak)):
                lst = create_detection_square(bot)
                MAY_CONTAIN_LEAK = intersection(MAY_CONTAIN_LEAK, lst)
                actions += 1
                break
            else: 
                MAY_CONTAIN_LEAK.remove((i,j))
            next_location = next_move(bot, MAY_CONTAIN_LEAK)
            actions += math.dist(next_location, bot)
            bot = next_location
    elif BOT == 2: 
        while bot != leak: 
            detections = []
            if(detect(bot, leak)):
                lst = create_detection_square(bot)
                detections.append(lst)
                MAY_CONTAIN_LEAK = intersection(MAY_CONTAIN_LEAK, lst)
                actions += 1
                break
            else: 
                MAY_CONTAIN_LEAK.remove(i,j)
                MAY_CONTAIN_LEAK = [(i,j) for (i,j) in MAY_CONTAIN_LEAK if i not in detections]
            next_location = next_move(bot, MAY_CONTAIN_LEAK)
            actions += math.dist(next_location, bot)
            bot = next_location
    return actions 

def probabilistic_search():
