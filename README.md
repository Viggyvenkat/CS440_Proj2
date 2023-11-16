# CS440_Proj2

1) For Bot 2, we designed the bot to only chose 50% of the cells that were checked by the detection method. This was chosen based on the intersection between May have leak and the robot locations for the x and y direction multiplied by the rate of change that was determined by the k value. For bot 4, we used detect for beep half the time. And for bot 9, we also used the underlying algorithm for bot 8 and we checked for leaks 50% of the time. 
2) The probabilities for 3/4 should be updated using the bayes theorem:
  P(at cell (x,y) given its NOT at (a,b)) = P(not at (a,b) given its at cell (x,y))*P(at cell (x,y))/P(not at cell (a,b)) P(at cell (x,y) given its NOT at (a,b)) = P(at cell (x,y))/P(not at cell (a,b)) = dict[(x,y)]/(1-dict[(a,b)])

P(at cell (x,y) given we got a beep)) = P(we get a beep given at cell (x,y))*P(at cell (x,y))/P(getting a beep)

P(at cell (x,y) given we not got a beep)) = P(we not get a beep given at cell (x,y))*P(at cell (x,y))/P(not getting a beep)

For 8/9: 

for each potential location of a leak, denote L(x,y) true if there is a leak at x,y.
we have 
P( L(x,y) given we heard a beep) = P(hear a beep given L(x,y))*P(L(x,y))/P(hear a beep)

P(hear a beep) is constant across all x,y , so we can just normalize at the end

If we know P(hear a beep from one leak), we have the solution

P(hear a beep given L(x,y)) = P(hear a beep FROM (x,y) to bot_loc)+P(hear a beep NOT from (x,y) to bot_loc) - P(hear a beep FROM (x,y) to bot_loc)*P(hear a beep NOT from (x,y) to bot_loc)


Prob(havent heard a beep
P(hear a beep) = x

P(hear a beep NOT from (x,y) to bot_loc) = x-P(hear beep from (x,y)

P(L(x,y) given heard no beep) = P(L(x,y) and (x,y) gives no beep))*P(no beep heard from elsewhere)
= P(L(x,y) and (x,y) gives no beep))*(prob_beep


P(beep heard from elsewhere) 
= prob(beep and beep not from (x,y))
know:
prob(beep and not considering x,y) + ((1-prob(beep and not considering x,y))*prob(beep from x,y)= prob_beep 
prob(beep and not considering x,y) + prob(beep from x,y) - prob(beep and not considering x,y)prob(beep from x,y)= prob_beep 
prob(beep and not considering x,y)(1-prob(beep from x,y)) + prob(beep from x,y) = prob_beep 
prob(beep and not considering x,y)(1-prob(beep from x,y)) = prob_beep - prob(beep from x,y)
prob(beep and not considering x,y) = (prob_beep - prob(beep from x,y))/((1-prob(beep from x,y)))

However, 3 and 4 were tested on a 50x50 grid and 7,8,9 were tested on a 20x20 grid. 

3) for 1 vs 2: bot 2 on average was 100 actions less than bot 1.
  for bot 3 vs 4: For both 3 vs 4, there is approximately a difference of 35 actions at an alpha value of 0.01. Whereas, when the alpha value scales to 0.1, bot 4 performs worse with an approximately 100 actions difference between bot 3 and 4. 
  for bot 5 vs 6: for both 5 vs 6, as the k value increases the number of actions between 6 and 5 increases, whereas 6 is always less than 5. When k = 1, there is about a 100 actions difference for a grid of 50 x 50, when the k values increases to 10 there is approximately a 1100 average difference and when the k value increases to 21, bot 2 performs worse than bot 1 with about a difference in 5000 actions. This can attributed to randomness. 
  for bot 7 vs 8 vs 9: 
5) Every iteration you should update the proability knowledge base but you should also have a detection square, thus inducing deterministic decisions alongside probabilisitc decisions. When deterministic decisions are closer to the leak, then chose 5,6 bots, whereas use probabilstic decisions to decide which cell is closer to the leak. so you bye pass some of the determinsistic inefficiencies. 
