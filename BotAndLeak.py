import PySimpleGUI as sg
import random
import time
import sys
import heapq
import math
from collections import deque

GRID_SIZE = 50
DISPLAY_TEST = False
BOT_TYPE =7
BOT_VISIBILITY = 0
ALPHA = 0.0
INF = 2**32-1
NUMBER_OF_ACTIONS = 0

# If run from RunBotAndFire.py, variables are updated and test is not displayed for efficiency
# Else, run simulation as normal
if len(sys.argv) == 4:
    GRID_SIZE = int(sys.argv[1])
    BOT_TYPE = int(sys.argv[2])
    if BOT_TYPE == 3 or BOT_TYPE == 4 or BOT_TYPE >= 7:
        ALPHA = float(sys.argv[3])
    else:
        BOT_VISIBILITY = int(sys.argv[3])
    DISPLAY_TEST = False
elif len(sys.argv) != 1:
    print("Usage: python your_script.py <GRID_SIZE>, <BOT_TYPE>")
    sys.exit(1)

# Colors of grid displayed
COLOR_ROBOT = 'darkblue'
COLOR_BACKGROUND = 'black'
COLOR_CORRIDOR = 'grey'
COLOR_LEAK = 'red'
COLOR_PATH = 'lightblue'
COLOR_IN_VIEW = 'white'
COLOR_POSSIBLE_LEAK = 'orange' # used as background color for bots 3,4,7,8,9

# fn for easy randomization from 1 to n-1
def rand(n):
    return random.randint(0,n-1)

# initializing first corridor cell
first_cell_x = rand(GRID_SIZE)
first_cell_y = rand(GRID_SIZE)

# dictionary of all cells that are not walls
corridor_dict = {
    (first_cell_x, first_cell_y): True
}

# initailization of necessary data structures
blocked_cells = []
dead_ends = {}
bot_queue = deque()
possible_leaks = {}
within_leak_perimeter = {}

def within_distance(loc1, loc2, distance):
    return abs(loc1[0]-loc2[0]) <= distance and abs(loc1[1]-loc2[1]) <= distance

# checks if a location is valid (within bounds)
def within_bounds(pair):
    i = pair[0]
    j = pair[1]
    return i >= 0 and i < GRID_SIZE and j >= 0 and j < GRID_SIZE

# true if (i,j) is currently blocked, and is adjacent to exactly one unblocked cell
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

# checks if a corridor location is a dead end
def dead_end(pair):
    i = pair[0]
    j = pair[1]
    cnt = 0
    if ((i+1),j) in corridor_dict: cnt += 1
    if ((i-1),j) in corridor_dict: cnt += 1
    if (i,(j+1)) in corridor_dict: cnt += 1
    if (i,(j-1)) in corridor_dict: cnt += 1
    return cnt == 1

# adds blocked cells adjacent to corridor location to queue
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
    
# returns random pair that is in corridor
def randValid():
    while True:
        loc = (rand(GRID_SIZE),rand(GRID_SIZE))
        if loc in corridor_dict: return loc

# determines if first leak_location and robot_location is an invalid starting position
def invalid_start():
    if BOT_TYPE <= 2 or BOT_TYPE == 5 or BOT_TYPE == 6:
        return within_distance(robot_location,leak_location,BOT_VISIBILITY)
    if BOT_TYPE == 3 or BOT_TYPE == 4:
        return robot_location == leak_location

# determines if the second leak location is invalid for the starting position
def second_invalid_start():
    if BOT_TYPE <= 4:
        return False
    return leak_location == second_leak_location or within_distance(robot_location,second_leak_location,BOT_VISIBILITY) 

# opens closed neighbors in random order
def open_closed_neighbor(pair):
    list = [(-1,0),(1,0),(0,-1),(0,1)]
    random.shuffle(list)
    for pair_2 in list:
        possible_pair = ((pair[0] + pair_2[0]), (pair[1]+pair_2[1]))
        if within_bounds(possible_pair) and possible_pair not in corridor_dict:
            to_be_added[possible_pair] = True
            break

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
        open_closed_neighbor(pair)
        
for pair,_ in to_be_added.items():
    corridor_dict[pair] = True

# initializes locations of robot and end location
robot_location = randValid()
robot_path = {} # all cells that robot plans on traversing through
leak_location = randValid()
second_leak_location = randValid()

while invalid_start():
    leak_location = randValid()
while second_invalid_start():
    second_leak_location = randValid()

if BOT_TYPE >= 5:
    leak_location = (leak_location,second_leak_location)
    
for i in range(GRID_SIZE):
    for j in range(GRID_SIZE):
        if not within_distance((i,j),robot_location,BOT_VISIBILITY):
            possible_leaks[(i,j)] = True


bot_data = {}
robot_path_list = deque()

best_cell = (-1,-1)
bot_data_length = {}

# Bot 2 will be designed to find the shortest path to discovering if a cell is the leak; i.e. optimizing for detecting through walls
# This will be implemented by creating a boolean dictionary for each cell, determining whether or not it is close enough to confirm/deny a potential leak, then DFSing to reach one True cell

def bot_1_2_detect_surroundings():
    global robot_location,NUMBER_OF_ACTIONS
    NUMBER_OF_ACTIONS += 1
    #if robot can detect that there is a leak nearby
    if within_distance(robot_location,leak_location,BOT_VISIBILITY):
        # remove all possible leaks other than ones in the range
        for (i,j) in possible_leaks.copy():
            if not within_distance(robot_location,(i,j),BOT_VISIBILITY):
                del possible_leaks[(i,j)]
    else:
        #remove all possible leaks that are in range of robot_location
        if robot_location in possible_leaks:
            del possible_leaks[robot_location]
        #remove all leaks that are in the range of deletion
        for i in range(BOT_VISIBILITY+1):
            for j in range(BOT_VISIBILITY+1):
                if i == 0 and j == 0:
                    continue
                deltas = [(1,1),(1,-1),(-1,-1),(-1,1),]
                for delta in deltas:
                    if((robot_location[0]+i*delta[0],robot_location[1]+j*delta[1])
                        in possible_leaks):
                        del possible_leaks[(robot_location[0]+i*delta[0],
                                            robot_location[1]+j*delta[1])]


def bot_5_6_detect_surroundings():
    global robot_location,NUMBER_OF_ACTIONS
    NUMBER_OF_ACTIONS += 1
    #if robot can detect that there is a leak nearby
    if within_distance(robot_location,leak_location[0],BOT_VISIBILITY) or (len(leak_location) != 1 and within_distance(robot_location,leak_location[1],BOT_VISIBILITY)):            
        # remove all possible leaks other than ones in the range
        for (i,j) in possible_leaks.copy():
            if not within_distance(robot_location,(i,j),BOT_VISIBILITY):
                del possible_leaks[(i,j)]
    else:
        #remove all possible leaks that are in range of robot_location
        if robot_location in possible_leaks:
            del possible_leaks[robot_location]
        #remove all leaks that are in the range of deletion
        for i in range(BOT_VISIBILITY+1):
            for j in range(BOT_VISIBILITY+1):
                if i == 0 and j == 0:
                    continue
                deltas = [(1,1),(1,-1),(-1,-1),(-1,1),]
                for delta in deltas:
                    if((robot_location[0]+i*delta[0],robot_location[1]+j*delta[1])
                        in possible_leaks):
                        del possible_leaks[(robot_location[0]+i*delta[0],
                                            robot_location[1]+j*delta[1])]
                    
def good_step_bot_1_2(location):
    return location in corridor_dict and location not in bot_data

# Creates robot_path_list: the path the bot plans on taking
def populate_bot_path(endpoint):
    tmp_iterator = endpoint

    while tmp_iterator in bot_data and bot_data[tmp_iterator] != tmp_iterator:
        robot_path_list.append(tmp_iterator)
        robot_path[tmp_iterator] = True
        tmp_iterator = bot_data[tmp_iterator]
    if tmp_iterator not in bot_data: 
        print(tmp_iterator,"NOT IN BOT_DATA")
        sys.exit(1)

def is_end_goal(curr_location,iteration):
    if BOT_TYPE == 1:
        return curr_location in possible_leaks
    if BOT_TYPE == 2:
        return curr_location in possible_leaks
    if BOT_TYPE == 3 or BOT_TYPE  == 4:
        if iteration == 0:
            return False
        if iteration == 1:
            return curr_location == best_cell
        if iteration == 2:
            return curr_location == leak_location
    if BOT_TYPE == 5:
        return curr_location in possible_leaks
    if BOT_TYPE == 6:
        return curr_location in possible_leaks
    if BOT_TYPE == 7 or BOT_TYPE == 8 or BOT_TYPE == 9:
        if iteration == 0:
            return False
        if iteration == 1:
            return curr_location == best_cell
        if iteration == 2:
            return curr_location in leak_location

# performs BFS on grid to find closest point that could be a leak
# populates bot_data and bot_data_length
def bot_bfs(iteration):
    
    global robot_location
    bot_data.clear()
    bot_data_length.clear()
    bot_data[robot_location] = robot_location
    bot_data_length[robot_location] = 0
    bot_queue = deque()
    bot_queue.append(robot_location)
    robot_path_list.clear()
    robot_path.clear()
    endpoint = None
    while len(bot_queue) != 0 and endpoint == None:
        currLoc = bot_queue.popleft()
        delta = [(-1,0),(1,0),(0,-1),(0,1)]
        for pair in delta:
            new_pair = (currLoc[0]+pair[0], currLoc[1]+pair[1])
            if good_step_bot_1_2(new_pair):
                bot_data[new_pair] = currLoc
                bot_data_length[new_pair] = bot_data_length[currLoc]+1
                bot_queue.append(new_pair)
                if is_end_goal(new_pair,iteration): 
                    endpoint = new_pair
                    break
    if BOT_TYPE <= 2 or ((BOT_TYPE == 3 or BOT_TYPE == 4) and iteration >= 1) or BOT_TYPE == 5 or BOT_TYPE == 6 or (BOT_TYPE >= 7 and iteration >= 1):
        populate_bot_path(endpoint)
        return robot_path_list[-1]
    return (-1,-1)
    
    
# for Bot 3, bot_data gives parent cell, and bot_data_length givesdistance from robot_location
probability_leak = {}
probability_leak[robot_location] = 0
for pair in corridor_dict:
    if pair == robot_location: continue
    probability_leak[pair] = 1.0/(len(corridor_dict)-1)
    
def probability_best_cell():
        
    global robot_location,probability_leak
    best_cell = robot_location
    for leak_loc in probability_leak:
        if probability_leak[leak_loc] > probability_leak[best_cell]:
            best_cell = leak_loc
            continue
        if probability_leak[leak_loc] == probability_leak[best_cell] and bot_data_length[leak_loc] < bot_data_length[best_cell]:
            best_cell = leak_loc

    return best_cell

def listen_for_beep():
    global robot_location,robot_path_list,ALPHA,NUMBER_OF_ACTIONS
    NUMBER_OF_ACTIONS += 1
    # distance is now bot_data_length[leak_location]
    d = bot_data_length[leak_location]
    prob_of_beep = math.pow(math.e,-1*ALPHA*(d-1))
    #check if beep occurs
    if(random.random() <= prob_of_beep):
        return True
    return False

def listen_for_beep_multiple_leaks():
    global robot_location,robot_path_list,ALPHA,NUMBER_OF_ACTIONS
    NUMBER_OF_ACTIONS += 1
    # distance is now bot_data_length[leak_location]
    for leak_loc in leak_location:
        d = bot_data_length[leak_loc]
        prob_of_beep = math.pow(math.e,-1*ALPHA*(d-1))
        #check if beep occurs
        if(random.random() <= prob_of_beep):
            return True
    return False
    
    
def update_probabilities():
    for location in probability_leak:
        if location == robot_location: continue
        probability_leak[location] = probability_leak[location]/(1.0-probability_leak[robot_location])
        
    probability_leak[robot_location] = 0

def update_probabilities_for_beep_bot_8_9():
    
    
    # saw a beep, so we need to calculate the prob of hearing a beep at all    
    
    # GOAL: get P(hear a beep NOT from (x,y) to bot_loc). To do so, we calculate P(hear a beep)
    prob_beep = 1
    for pair in probability_leak:
        if probability_leak[pair] == 0:
            continue
        
        d = bot_data_length[pair]
        prob_of_beep = math.pow(math.e,-1*ALPHA*(d-1))
        # only add prob that we havent heard a beep yet * prob of beep to avoid overlap
        prob_beep *= (1-prob_of_beep)
        
    prob_beep = 1-prob_beep
        
    # P(beep given (x,y) is leak) = P(beep from (x,y) + P(beep from elsewhere)- P(beep from (x,y) and beep from elsewhere)
    # = prob_of_beep + ((prob_beep - prob(beep from x,y))/((1-prob(beep from x,y)))) - ((prob_beep - prob(beep from x,y))/((1-prob(beep from x,y))))*prob_of_beep
    # = prob_of_beep + ((prob_beep - prob_of_beep)/((1-prob_of_beep))) - ((prob_beep - prob_of_beep)/((1-prob_of_beep)))*prob_of_beep
    # math is in writeup

    
    # P( L(x,y) given we heard a beep) = P(hear a beep given L(x,y))*P(L(x,y))/P(hear a beep)
    # P(hear a beep) is constant across all x,y , so we can just normalize at the end
    
    
    # P(we get a beep given its at cell (x,y)), so we used bot_bfs to populate bot_data_length
    sum = 0.0
    for pair in probability_leak:
        if probability_leak[pair] == 0:
            continue
        # distance is now bot_data_length[leak_location]
        d = bot_data_length[pair]
        prob_of_beep = math.pow(math.e,-1*ALPHA*(d-1))
        if prob_of_beep == 1:
            probability_leak[pair] = 0
        else:
            mult_value = prob_of_beep + prob_of_beep + ((prob_beep - prob_of_beep)) - ((prob_beep - prob_of_beep))*prob_of_beep

            # mult_value = prob_of_beep + prob_of_beep + ((prob_beep - prob_of_beep)/((1-prob_of_beep))) - ((prob_beep - prob_of_beep)/(1-prob_of_beep))*prob_of_beep
            probability_leak[pair] *= mult_value
        sum += probability_leak[pair]
    
    #sum should be 1 (by dividing by P(getting a beep)), so we normalize by dividing by sum
    for pair in probability_leak:
        probability_leak[pair] /= sum
        
def update_probabilities_for_no_beep_bot_8_9():
    # logic very similar to update_probabilities_for_beep_bot_8_9()
    
    prob_beep = 1
    for pair in probability_leak:
        if probability_leak[pair] == 0:
            continue
        
        d = bot_data_length[pair]
        prob_of_beep = math.pow(math.e,-1*ALPHA*(d-1))
        # only add prob that we havent heard a beep yet * prob of beep to avoid overlap
        prob_beep *= (1-prob_of_beep)
        
    prob_beep = 1-prob_beep
        
    # P(no beep given L(x,y)) = P(no beep from (x,y) + P(no beep from elsewhere)- P(no beep from (x,y) and no beep from elsewhere)
    # = (1-prob_of_beep) + (1- ((prob_beep - prob(beep from x,y))/((1-prob(beep from x,y))))) - (1-prob_of_beep) * (1- ((prob_beep - prob(beep from x,y))/((1-prob(beep from x,y)))))
    # = (1-prob_of_beep) + (1- ((prob_beep - prob_of_beep)/((1-prob_of_beep)))) - (1-prob_of_beep) * (1- ((prob_beep - prob_of_beep)/((1-prob_of_beep))))
    
    sum = 0.0
    for pair in probability_leak:
        if probability_leak[pair] == 0:
            continue
        # distance is now bot_data_length[leak_location]
        d = bot_data_length[pair]
        prob_of_beep = math.pow(math.e,-1*ALPHA*(d-1))
        if prob_of_beep == 1:
            probability_leak[pair] = 0
        else:
            mult_value = (1-prob_of_beep) + (1- ((prob_beep - prob_of_beep))) - (1-prob_of_beep) * (1- ((prob_beep - prob_of_beep)))
            # mult_value = (1-prob_of_beep) + (1- ((prob_beep - prob_of_beep)/((1-prob_of_beep)))) - (1-prob_of_beep) * (1- ((prob_beep - prob_of_beep)/(1-prob_of_beep)))
            probability_leak[pair] *= mult_value
        sum += probability_leak[pair]
    
    #sum should be 1 (by dividing each prob by P(getting a beep)), so we normalize by dividing by sum
    for pair in probability_leak:
        if probability_leak[pair] == 0:
            continue
        probability_leak[pair] /= sum

def update_probabilities_for_beep():
    # saw a beep, so we need to calculate the prob of hearing a beep at all    
    
    # P(we get a beep given its at cell (x,y)), so we used bot_bfs to populate bot_data_length
    sum = 0.0
    for pair in probability_leak:
        if probability_leak[pair] == 0:
            continue
        # distance is now bot_data_length[leak_location]
        d = bot_data_length[pair]
        prob_of_beep = math.pow(math.e,-1*ALPHA*(d-1))
        probability_leak[pair] *= prob_of_beep
        sum += probability_leak[pair]
    
    #sum should be 1 (by dividing by P(getting a beep)), so we normalize by dividing by sum
    for pair in probability_leak:
        probability_leak[pair] /= sum
        
def update_probabilities_for_no_beep():
    # saw a beep, so we need to calculate the prob of hearing a beep at all    
    
    # P(we get a beep given its at cell (x,y)), so we used bot_bfs to populate bot_data_length
    sum = 0.0
    for pair in probability_leak:
        if probability_leak[pair] == 0:
            continue
        # distance is now bot_data_length[leak_location]
        d = bot_data_length[pair]
        prob_of_no_beep = 1 - math.pow(math.e,-1*ALPHA*(d-1))
        probability_leak[pair] *= prob_of_no_beep
        sum += probability_leak[pair]
    
    #sum should be 1 (by dividing by P(getting a beep)), so we normalize by dividing by sum
    for pair in probability_leak:
        probability_leak[pair] /= sum
        
    
def bot_2_6_poss_leaks_in_range():
    cnt = 0
    for i in range(BOT_VISIBILITY+1):
            for j in range(BOT_VISIBILITY+1):
                if i == 0 and j == 0:
                    continue
                deltas = [(1,1),(1,-1),(-1,-1),(-1,1),]
                for delta in deltas:
                    if((robot_location[0]+i*delta[0],robot_location[1]+j*delta[1])
                        in possible_leaks):
                        cnt += 1
    
    return cnt

def bot_9_run():
    global robot_location,leak_location,possible_leaks,NUMBER_OF_ACTIONS,best_cell
    
    # for i in range(GRID_SIZE):
    #     for j in range(GRID_SIZE):
    #         if (i,j) not in probability_leak:
    #             print("\t", end="")
    #         else:
    #             print(f"{probability_leak[(i,j)]:.5f} ",end="")
    #     print("")
    next_location = bot_bfs(0)

    best_cell = probability_best_cell()
    next_location = bot_bfs(1)
    
    robot_location = next_location
    
    if robot_location in leak_location:
        leak_location = tuple(item for item in leak_location if item != robot_location)
        if leak_location == ():
            return
    
    # Not at leak location, so must update probabilities
    update_probabilities()
    bot_bfs(0)
    #listen for chirp only 30% of the time
    if random.random() <= 0.3:
        if listen_for_beep_multiple_leaks():
            # print("BEEP!")
            update_probabilities_for_beep_bot_8_9()
        else:
            # print("NO BEEP!")
            update_probabilities_for_no_beep_bot_8_9()

def bot_8_run():
    global robot_location,leak_location,possible_leaks,NUMBER_OF_ACTIONS,best_cell
    
    # for i in range(GRID_SIZE):
    #     for j in range(GRID_SIZE):
    #         if (i,j) not in probability_leak:
    #             print("\t", end="")
    #         else:
    #             print(f"{probability_leak[(i,j)]:.5f} ",end="")
    #     print("")
    next_location = bot_bfs(0)

    best_cell = probability_best_cell()
    next_location = bot_bfs(1)
    
    robot_location = next_location
    
    if robot_location in leak_location:
        leak_location = tuple(item for item in leak_location if item != robot_location)
        if leak_location == ():
            return
    
    # Not at leak location, so must update probabilities
    update_probabilities()
    bot_bfs(0)
    #listen for chirp
    if listen_for_beep_multiple_leaks():
        # print("BEEP!")
        update_probabilities_for_beep_bot_8_9()
    else:
        # print("NO BEEP!")
        update_probabilities_for_no_beep_bot_8_9()

def bot_7_run():
    global robot_location,leak_location,possible_leaks,NUMBER_OF_ACTIONS,best_cell
    next_location = bot_bfs(0)

    best_cell = probability_best_cell()
    next_location = bot_bfs(1)
    
    robot_location = next_location
    
    if robot_location in leak_location:
        leak_location = tuple(item for item in leak_location if item != robot_location)
        if leak_location == ():
            return
    
    # Not at leak location, so must update probabilities
    update_probabilities()
    bot_bfs(0)
    #listen for chirp
    if listen_for_beep_multiple_leaks():
        update_probabilities_for_beep()
    else:
        update_probabilities_for_no_beep()

def bot_6_run():
    global robot_location,leak_location,possible_leaks,NUMBER_OF_ACTIONS,best_cell
    next_location = bot_bfs(0)
    robot_location = next_location
    NUMBER_OF_ACTIONS += 1
    
    if robot_location in leak_location:
        leak_location = tuple(item for item in leak_location if item != robot_location)
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                possible_leaks[(i,j)] = True
        return
    
    if robot_location in possible_leaks:
        del possible_leaks[robot_location]
    
    thirty_percent = 0.3*((2*BOT_VISIBILITY+1)*(2*BOT_VISIBILITY+1)-1)
    possible_cells_in_range = bot_2_6_poss_leaks_in_range()
    
    # only check if there are sufficient cells of both type, so any data is useful
    if possible_cells_in_range >= thirty_percent:
        bot_5_6_detect_surroundings()

def bot_5_run():
    global robot_location,leak_location,possible_leaks,NUMBER_OF_ACTIONS,best_cell
    next_location = bot_bfs(0)
    robot_location = next_location
    NUMBER_OF_ACTIONS += 1
    
    if robot_location in leak_location:
        leak_location = tuple(item for item in leak_location if item != robot_location)
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                possible_leaks[(i,j)] = True
        return
    
    if robot_location in possible_leaks:
        del possible_leaks[robot_location]
    
    bot_5_6_detect_surroundings()
    
def bot_4_run():
    global robot_location,possible_leaks,NUMBER_OF_ACTIONS,best_cell
    next_location = bot_bfs(0)
    
    best_cell = probability_best_cell()
    next_location = bot_bfs(1)
    
        
    robot_location = next_location
    NUMBER_OF_ACTIONS += 1
    
    if robot_location == leak_location:
        return
    
    update_probabilities()
    #approx 50% of the time, check for beeps
    if random.random() <= 0.5 :
        # Not at leak location, so must update probabilities
        bot_bfs(0)
        #listen for chirp
        if listen_for_beep():
            update_probabilities_for_beep()
        else:
            update_probabilities_for_no_beep()

def bot_3_run():
    global robot_location,leak_location,possible_leaks,NUMBER_OF_ACTIONS,best_cell
    next_location = bot_bfs(0)

    best_cell = probability_best_cell()
    next_location = bot_bfs(1)
    
    robot_location = next_location
    NUMBER_OF_ACTIONS += 1
    
    if robot_location == leak_location:
        return
    
    # Not at leak location, so must update probabilities
    update_probabilities()
    bot_bfs(0)
    #listen for chirp
    if listen_for_beep():
        update_probabilities_for_beep()
    else:
        update_probabilities_for_no_beep()
 
# bot 2 is identical to bot 1, however it only checks its surroundings if at least 30% of its visibility could be the leak    
def bot_2_run():
    global robot_location,possible_leaks,NUMBER_OF_ACTIONS,best_cell
    next_location = bot_bfs(0)
    robot_location = next_location
    NUMBER_OF_ACTIONS += 1
    
    if robot_location == leak_location:
        return
    
    if robot_location in possible_leaks:
        del possible_leaks[robot_location]
    
    thirty_percent = 0.3*((2*BOT_VISIBILITY+1)*(2*BOT_VISIBILITY+1)-1)
    possible_cells_in_range = bot_2_6_poss_leaks_in_range()
    
    # only check if there are sufficient cells of that could be leak, so any data is useful
    if possible_cells_in_range >= thirty_percent:
        bot_1_2_detect_surroundings()

# bot 1 searches for the closest possible leak, then moves towards it
# At every action, it also checks to see if the leak is within visibility distance
def bot_1_run():
    global robot_location,possible_leaks,NUMBER_OF_ACTIONS,best_cell
    
    # performs bfs on grid to find closest potential leak. This costs 1 action
    robot_location = bot_bfs(0)
    NUMBER_OF_ACTIONS += 1
    
    if robot_location == leak_location:
        return
    
    # robot cannot be on a leak, so remove it
    if robot_location in possible_leaks:
        del possible_leaks[robot_location]
    
    # checks surroundings for leak in visibility
    bot_1_2_detect_surroundings()

# which color a cell should be
def which_color(i,j):
    if (i,j) == robot_location:
        return COLOR_ROBOT
    if (i,j) == leak_location or (i,j) in leak_location:
        return COLOR_LEAK
    if (i,j) in robot_path:
        return COLOR_PATH
    if (i,j) not in corridor_dict:
        return COLOR_BACKGROUND
    if (i,j) in possible_leaks:
        return COLOR_POSSIBLE_LEAK
    if within_distance((i,j),robot_location,BOT_VISIBILITY):
        return COLOR_IN_VIEW
    return COLOR_CORRIDOR


# if the sim is being displayed, initialize display layout
if DISPLAY_TEST:
    grid_layout = [[sg.Text('', size=(2,1), background_color=which_color(i,j), pad=(0,0), key=(i,j)) 
            for j in range(GRID_SIZE)] for i in range(GRID_SIZE)]

    start_button_layout = [[
        sg.Button('Start', size=(10, 1)),
        sg.Text('Turns Per Second: '),
        sg.InputText('', size=(10, 1), key='simulation_speed')
    ]]

    layout = [
        [sg.Column(grid_layout, pad=(0, 0))],
        [sg.Column(start_button_layout)],
    ]
    window = sg.Window('Grid Example', layout)


# Waits for simulation speed input if displaying
while True and DISPLAY_TEST:
    event, values = window.read()
    if event == 'Start':
        break

# Sets simulation speed that was just given
if DISPLAY_TEST:
    refresh_rate = 1.0 / float(values['simulation_speed'])

try:
    # runs simulation until robot reached all leak locations
    while True:
        if(robot_location == leak_location or robot_location in leak_location or leak_location == ()): sys.exit(0)
        
        #Executes right kind of bot behavior
        if BOT_TYPE == 1:
            bot_1_run()
        elif BOT_TYPE == 2:
            bot_2_run()
        elif BOT_TYPE == 3:
            bot_3_run()
        elif BOT_TYPE == 4:
            bot_4_run()
        elif BOT_TYPE == 5:
            bot_5_run()
        elif BOT_TYPE == 6:
            bot_6_run()
        elif BOT_TYPE == 7:
            bot_7_run()
        elif BOT_TYPE == 8:
            bot_8_run()
        elif BOT_TYPE == 9:
            bot_9_run()
            
        # Changes display
        if DISPLAY_TEST:
            time.sleep(refresh_rate)
            for i in range(GRID_SIZE):
                for j in range(GRID_SIZE):
                    window[(i,j)].update(background_color=which_color(i,j))

            window.refresh()
finally:
    print(NUMBER_OF_ACTIONS)
    
    
