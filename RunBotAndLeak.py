import subprocess
import threading

# 20 sets of NUM_TESTS run
NUM_TESTS = 500
python_script = "BotAndLeak.py"
arg1 = 100
arg2 = 0.00
arg3 = 1
num_success = 0
results_num = {}
results_prob = {}

# runs simulation of BotAndFire.py
def run_subprocess():
    global num_success
    command = ["python3", python_script, str(arg1), str(arg2), str(arg3)]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        num_success += 1

# Iterates through bots
for j in range(1):
    print(f'BOT {arg3}')
    
    # Iterates through FIRE_PROB
    for i in range(21):
        threads = []
        num_success = 0

        # Runs 10000 test cases
        for i in range(20):
            for _ in range(NUM_TESTS):
                thread = threading.Thread(target=run_subprocess)
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()
            # print((i+1),"/20 : ", num_success)
        
        # Prints success rates
        formatted_arg2 = "{:.2f}".format(arg2)
        probability_success = "{:.5f}".format(float(num_success)/NUM_TESTS)
        results_num[(str(arg3), formatted_arg2)] = num_success 
        results_prob[(str(arg3), formatted_arg2)] = probability_success 
        print(f'{formatted_arg2} : {num_success} : {probability_success}')
        arg2 += 0.05
    arg2 = 0
    arg3 += 1
            
# print(results_num['1','1.50'])
# with open('BotAndFireData.txt', 'w') as file:
#     file.write(f'NUMBER OF TESTS PER FIRE_PROB: {NUM_TESTS}\n\n')
#     file.write('Fire_Prob\tBot 1 Wins\tBot 2 Wins\tBot 3 Wins\n')
#     p = 0.0
#     for i in range(21):
#         prob = "{:.2f}".format(p)
#         file.write(f'{prob}\t\t{results_num[("1",prob)]}\t\t\t{results_num[("2",prob)]}\t\t\t{results_num[("3",prob)]}\n')
#         p += 0.05
    
#     file.write('\nFire_Prob\tBot 1 Prob\tBot 2 Prob\tBot 3 Prob\n')
#     p = 0.0
#     for i in range(21):
#         prob = "{:.2f}".format(p)
#         file.write(f'{prob}\t\t{results_prob[("1",prob)]}\t\t{results_prob[("2",prob)]}\t\t{results_prob[("3",prob)]}\n')
#         p += 0.05

    
        
