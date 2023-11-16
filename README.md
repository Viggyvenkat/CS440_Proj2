# CS440_Proj2

1) For Bot 2, we designed the bot to only chose 50% of the cells that were checked by the detection method. This was chosen based on the intersection between May have leak and the robot locations for the x and y direction multiplied by the rate of change that was determined by the k value. For bot 4, we used detect for beep half the time. And for bot 9, we also used the underlying algorithm for bot 8 and we checked for leaks 50% of the time. 
2) The probabilities for 3/4 should be updated using the bayes theorem:
  P(at cell (x,y) given its NOT at (a,b)) = P(not at (a,b) given its at cell (x,y))*P(at cell (x,y))/P(not at cell (a,b)) P(at cell (x,y) given its NOT at (a,b)) = P(at cell (x,y))/P(not at cell (a,b)) = dict[(x,y)]/(1-dict[(a,b)])

P(at cell (x,y) given we got a beep)) = P(we get a beep given at cell (x,y))*P(at cell (x,y))/P(getting a beep)

P(at cell (x,y) given we not got a beep)) = P(we not get a beep given at cell (x,y))*P(at cell (x,y))/P(not getting a beep)

For 8/9: 

3) 
4) Every iteration you should update the proability knowledge base but you should also have a detection square, thus inducing deterministic decisions alongside probabilisitc decisions. When deterministic decisions are closer to the leak, then chose 5,6 bots, whereas use probabilstic decisions to decide which cell is closer to the leak. so you bye pass some of the determinsistic inefficiencies. 
