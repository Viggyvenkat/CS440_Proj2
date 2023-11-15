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

to_be_added = []

# Assuming `corridor_dict` and functions like `dead_end` and `open_closed_neighbor` are defined

for pair, _ in list(corridor_dict.items()):
    if dead_end(pair) and rand(2) == 1:
        open_closed_neighbor(corridor_dict, pair)
        to_be_added.append(pair)

for pair in to_be_added:
    corridor_dict[pair] = True

def randValid():
    while True:
        loc = (rand(GRID_SIZE),rand(GRID_SIZE))
        if loc in corridor_dict: return loc

def leakRandValid(bot, k):
    while True:
        loc = (rand(GRID_SIZE),rand(GRID_SIZE))
        if loc in corridor_dict: 
            if check_cells_around(bot, loc, k):
                return leakRandValid(bot, k)
            else:
                return loc

def check_cells_around(bot, leak, k):
    for i in range(bot[0] - k, bot[0] + k + 1):
        for j in range(bot[1] - k, bot[1] + k + 1):
            if((i,j) == leak):
                return True
    return False

def create_detection_square(bot, k ):
    lst = []
    for i in range(1, 2):
        for j in range(1, 2):
            lst.append((i * k * bot[0]), (j * k * bot[1]))
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

def deterministic_search(k: int):
    bot = randValid()
    leak = leakRandValid(bot, k)
    MAY_CONTAIN_LEAK = []

    for i,j in corridor_dict:
        if (i,j) == bot:
            continue
        MAY_CONTAIN_LEAK.append((i,j))
    
    actions = 0
    if BOT == 1:
        while bot != leak: 
            if(check_cells_around(bot, k, leak)):
                lst = create_detection_square(bot, k )
                MAY_CONTAIN_LEAK = intersection(MAY_CONTAIN_LEAK, lst)
                actions += 1
            else: 
                MAY_CONTAIN_LEAK.remove(bot)
            next_location = next_move(bot, MAY_CONTAIN_LEAK)
            actions += math.dist(next_location, bot)
            bot = next_location
    elif BOT == 2: 
        while bot != leak: 
            detections = []
            if(check_cells_around(bot, leak)):
                lst = create_detection_square(bot)
                detections.append(lst)
                MAY_CONTAIN_LEAK = intersection(MAY_CONTAIN_LEAK, lst)
                actions += 1
            else: 
                MAY_CONTAIN_LEAK.remove(i,j)
                MAY_CONTAIN_LEAK = [(i,j) for (i,j) in MAY_CONTAIN_LEAK if i not in detections]
            next_location = next_move(bot, MAY_CONTAIN_LEAK)
            actions += math.dist(next_location, bot)
            bot = next_location
    return actions 

''' 
def bot_enters_cell_probability(probability_matrix, bot_location):
    # P( leak in cell j | leak not found in bot_location )
    new_probability_matrix = probability_matrix
    b = 0

    new_probability_matrix[bot_location] = b
    for key in new_probability_matrix:
        a = new_probability_matrix[key]
        update_prob = (b * (b * a)) / a
        new_probability_matrix[key] = update_prob

    return new_probability_matrix 
 
def beep_probability_update():
    #P( leak in cell j | heard beep in bot_location )


def no_beep_probability_update():
    #P( leak in cell j | heard no beep in bot_location )

def get_location_of_max_probability(probability_matrix):
    maximum_prob = 0
    for key in probability_matrix:
        if maximum_prob < probability_matrix[key]:
            maximum_prob = probability_matrix[key]
    return maximum_prob

def plan_path_from_to(bot, next_location):
    lst = []
    for i in range(bot[0], next_location[0]):
        for j in range(bot[1], next_location[1]):
            lst.append((i,j))
    return lst        

def probabilistic_search(alpha: float):
    bot = randValid()
    leak = leakRandValid()
    probability_matrix = {}

    for (i,j) in corridor_dict:
        if (i,j) == bot:
            continue
        prob = {(i,j): 1/len(corridor_dict)}
        probability_matrix.update(prob)
    
    actions = 0 
    if BOT == 3: 
        while bot != leak:
            probability_matrix = bot_enters_cell_probability(probability_matrix, bot)
            shortest_distance = math.dist(leak, bot)
            beep = math.pow(math.e, alpha * (shortest_distance - 1))
            actions+=1

            if(beep > random()):
                probability_matrix = beep_probability_update(probability_matrix, bot)
            else: 
                probability_matrix = no_beep_probability_update(probability_matrix, bot)
            
            next_location = get_location_of_max_probability(probability_matrix)
            path = plan_path_from_to(bot, next_location)

            for (i,j) in path:
                bot = (i,j)
                if bot == leak: 
                    return actions
                else: 
                    probability_matrix = bot_enters_cell_probability(probability_matrix, bot)
                actions+=1
        return actions 
    
    elif BOT == 4: 


def deterministic_multiple_leaks():
    bot = randValid()
    leak1 = leakRandValid()
    leak2 = leakRandValid()
    MAY_CONTAIN_LEAK_1 = []
    MAY_CONTAIN_LEAK_2 = []

    actions = 0
    if BOT == 5:
        while bot != leak1 and bot != leak2: 
            if(detect(bot, leak1)):
                lst = create_detection_square(bot)
                MAY_CONTAIN_LEAK_1 = intersection(MAY_CONTAIN_LEAK_1, lst)
                actions += 1
            elif(detect(bot, leak2)):
                lst = create_detection_square(bot)
                MAY_CONTAIN_LEAK_2 = intersection(MAY_CONTAIN_LEAK_2, lst)
                actions += 1
            else: 
                MAY_CONTAIN_LEAK_1.remove(bot)
                MAY_CONTAIN_LEAK_2.remove(bot)
            next_location = next_move(bot, MAY_CONTAIN_LEAK)
            actions += math.dist(next_location, bot)
            bot = next_location

    elif BOT == 6:
        while bot != leak1 and bot != leak2: 
            detections = []
            if(detect(bot, leak1)):
                lst = create_detection_square(bot)
                detections.append(lst)
                MAY_CONTAIN_LEAK_1 = intersection(MAY_CONTAIN_LEAK_1, lst)
                actions += 1
            elif(detect(bot, leak2)):
                lst = create_detection_square(bot)
                detections.append(lst)
                MAY_CONTAIN_LEAK_2 = intersection(MAY_CONTAIN_LEAK_2, lst)
                actions += 1
            else: 
                MAY_CONTAIN_LEAK_1.remove(bot)
                MAY_CONTAIN_LEAK_2.remove(bot)
                MAY_CONTAIN_LEAK_1 = [(i,j) for (i,j) in MAY_CONTAIN_LEAK_1 if i not in detections]
                MAY_CONTAIN_LEAK_2 = [(i,j) for (i,j) in MAY_CONTAIN_LEAK_2 if i not in detections]

            next_location = next_move(bot, MAY_CONTAIN_LEAK_1)
            actions += math.dist(next_location, bot)
            bot = next_location
    return actions

def probabilistic_multiple_leaks():
    if BOT == 7:


    elif BOT == 8: 
    
    elif BOT == 9: 
'''

if __name__ == "__main__":
    actions = 0
    if BOT == 1 or BOT == 2:
        actions = deterministic_search(k = 1)
    '''
    elif BOT == 3 or BOT == 4: 
        actions = probabilistic_search()
    elif BOT == 5 or BOT == 6: 
        actions = deterministic_multiple_leaks()
    else:
        actions = probabilistic_multiple_leaks()
    '''
