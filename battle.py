
import random,time
import numpy as np
import bit_coding as bc
import bit_coding_test as bt
import bit_coding_battle as bb
import bit_coding_basic_time_control as btc
import bit_coding_test_SMCOnly as bsmc
import bit_coding_test_reinOnly as brein
import bit_coding_new as bn
import bit_coding_test_SMCOnly_even as bsmce
import pickle
from bit_coding_test import minimax_dict_test

"""
Head-to-head experiment runner for the 3D Connect Four dissertation.

This script imports the different agent implementations used in the
experimental comparisons, including:

- Basic fixed-depth minimax
- Improved fixed-depth minimax
- SMC-inspired adaptive-depth minimax
- Depth-aware experience reuse
- Combined SMC + experience reuse
- Odd/even-depth SMC variants

The individual search implementations are contained in the corresponding
bit_coding_*.py modules.
"""



test_episodes = 500
max_steps = 64


data_collect_smc = {}
win_inform = {}

def minimax_choose_Improve_score_function(depth,w_self2, w_self3, w_opp2, w_opp3):
    return bc.choose_best_move_dict(p1, p2, current_player, depth, alpha_m, beta_m,w_self2, w_self3, w_opp2, w_opp3)

def min_new(depth,w_self2, w_self3, w_opp2, w_opp3):
    return bn.choose_best_move_dict(p1, p2, current_player, depth, alpha_m, beta_m,w_self2, w_self3, w_opp2, w_opp3)

#===================base line===========================

def minimax_choose_basic_score_function(depth,w_self2, w_self3, w_opp2, w_opp3):
    return bb.choose_best_move_dict(p1, p2, current_player, depth, alpha_m, beta_m,w_self2, w_self3, w_opp2, w_opp3)

#===================base line===========================

def minimax_fix_time(w_self2, w_self3, w_opp2, w_opp3):
    return btc.choose_best_move_dict(p1,p2, current_player, alpha_m,beta_m,w_self2, w_self3, w_opp2, w_opp3, min_depth=3)

def minimax_pure_smc_odd(w_self2, w_self3, w_opp2, w_opp3, min_depth,time_limit):
    return bsmc.choose_best_move_dict(p1, p2, current_player, alpha_m, beta_m,w_self2, w_self3, w_opp2, w_opp3, min_depth, time_limit)


def minimax_pure_smc_even(w_self2, w_self3, w_opp2, w_opp3, min_depth,time_limit):
    return bsmce.choose_best_move_dict(p1, p2, current_player, alpha_m, beta_m,w_self2, w_self3, w_opp2, w_opp3, min_depth, time_limit)

def minimax_pure_rein(w_self2, w_self3, w_opp2, w_opp3):
    return brein.choose_best_move_dict(p1,p2, current_player, alpha_m,beta_m,w_self2, w_self3, w_opp2, w_opp3)

def minimax_choose_rein_smc(w_self2, w_self3, w_opp2, w_opp3,min_depth,time_limit):
    return bt.choose_best_move_dict(p1, p2, current_player, alpha_m, beta_m,w_self2, w_self3, w_opp2, w_opp3,min_depth,time_limit)

def save_mdict_table(minimax_dict, path="minimax_dict.pkl"):
    with open(path, "wb") as f:
        pickle.dump(minimax_dict, f)

def load_mdict_table(path="minimax_dict.pkl"):
    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return {}

def fair_order_rate(test_episodes):
    order_list = [] # 1,2,1,2,1...
    for i in range(test_episodes):
        if (i % 2) == 0:
            order_list.append(1)
        else:
            order_list.append(2)
    return order_list



def mcts_choose():
    return bc.mcts_search(p1, p2, current_player, time_limit=0.3, return_depth=False)

if __name__ == "__main__":
    order_list = fair_order_rate(test_episodes)
    minimax_win_N = 0
    battle_win_N = 0
    minimax_win_20N = 0
    battle_win_20N = 0
    minimax_win_steps = []
    battle_win_steps = []
    m_first = 0
    b_first = 0
    smc_timelimit_p1 = 0.1
    smc_timelimit_p2 = 0.1
    #print(len(minimax_dict_test))

    for c in range(test_episodes):
        p1 = 0
        p2 = 0
        current_player = 1
        alpha_m = -float("inf")
        beta_m = float("inf")
        #battle_position = random.randint(1,2)
        #battle_position = 2
        battle_position = order_list[c]
        if battle_position == 1:
            b_first += 1
            m_position = 2
        else:
            m_first += 1
            m_position = 1



        for max_step in range(max_steps):

            #valid_actions = rc.get_valid_actions(p1, p2)

            #if not valid_actions:
                #break

            if current_player == m_position:
                # name: minimax 1
                player = "minimax 1"
                #print("1")
                #print(f"smc time: {smc_timelimit_p1}")

                start_time = time.time()

                #position, new_depth_p1, smc_timelimit = minimax_choose_rein_smc(50, 600, 60, 1800,1,smc_timelimit)
                #position, new_depth_p1,smc_timelimit_p1 = minimax_pure_smc_odd(50, 600, 60, 1200, 3,smc_timelimit_p1)
                #position, new_depth_p1, smc_timelimit_p1 = minimax_pure_smc_even(50, 600, 60, 1200, 4, smc_timelimit_p1)
                position = minimax_choose_Improve_score_function(3,50, 600, 60, 1200)
                #position = minimax_choose_basic_score_function(3,50, 1000, 60, 1800)
                #position = minimax_pure_rein(50, 600, 60, 1200)

                #position = min_new(3, 50, 600, 60, 1200)

                end_time = time.time()

                total_time_p1 = (end_time - start_time)
                #key = (c, max_step)
                #data_collect_smc[key] = {"player: ": player, "depth": new_depth_p1, "time": total_time_p1, "time limit": smc_timelimit_p1}
                #print("depth: ", new_depth_p1)
                print(f"time: {end_time - start_time}\n")
            else:
                # name:  minimax 2
                player = "minimax 2"
                print("2")
                print(f"smc time: {smc_timelimit_p2}")
                start_time = time.time()

                #position, new_depth_p2, smc_timelimit_p2 = minimax_choose_rein_smc(50, 600, 60, 1200,3,smc_timelimit_p2)
                position, new_depth_p2,smc_timelimit_p2,node_count = minimax_pure_smc_odd(50, 600, 60, 1200, 3,smc_timelimit_p2)
                #position = minimax_choose_Improve_score_function(4, 50, 800, 60, 1800)
                #position, new_depth_p2, smc_timelimit_p2,node_count = minimax_pure_smc_even(50, 600, 60, 1200, 4, smc_timelimit_p2)
                #position = min_new(6,50, 600, 60, 1200)

                #position = minimax_pure_rein(50, 600, 60, 1200)

                end_time = time.time()

                total_time_p2 = (end_time - start_time)
                key = (c,max_step)
                data_collect_smc[key] = {"player: ": player, "depth": new_depth_p2, "time": end_time - start_time, "time limit": smc_timelimit_p2, "nodes explore": node_count}
                print("round: ", max_step)
                print("depth: ", new_depth_p2)
                print("nodes explore: ", node_count)
                print(f"time: {end_time - start_time}\n")







            p1, p2 = bc.play_position(p1, p2, current_player, position)
            if p1 & p2 != 0:
                print("oh noooooooooooo")#debug


            if bc.win(p1, p2, current_player):
                print("Round: ", c)
                if current_player == m_position:
                    minimax_win_N += 1
                    minimax_win_20N += 1
                    minimax_win_steps.append(max_step)
                    win_inform[c] = {"p1: ": 1, "p2: ": -1, "p1 order": m_position,"p2 order": battle_position, "win step: ": max_step, "order: ": current_player}
                    print(f"Player minimax wins! step: {max_step} order: {m_position}")
                else:
                    battle_win_N += 1
                    battle_win_20N += 1
                    battle_win_steps.append(max_step)
                    win_inform[c] = {"p1: ": -1, "p2: ": 1,"p1 order": m_position,"p2 order": battle_position, "win step: ": max_step, "order: ": current_player}
                    print(f"Player battle_position wins! step: {max_step} order: {battle_position}")

                break

            elif bt.draw(p1, p2, player):
                print("Round: ", c)
                win_inform[c] = {"p1: ": 0, "p2: ": 0, "p1 order": m_position,"p2 order": battle_position, "win step: ": 64, "order: ": current_player}

            current_player = bc.other_player(current_player)

        if (c+1) % 20 == 0:
            wr1 = minimax_win_20N / 20
            wr2 = battle_win_20N /20
            win_inform[c].update({"winning rate p1": wr1, "winning rate p2": wr2 })
            minimax_win_20N = 0
            battle_win_20N = 0

        if (c+1) % 50 == 0:
            save_mdict_table(data_collect_smc, path="data_collect.pkl")
            save_mdict_table(win_inform, path="win_inform.pkl")
            save_mdict_table(minimax_dict_test, path="minimax_dict_test.pkl")

    print(f"minimax 1 winning times: {minimax_win_N}   average steps: {np.mean(minimax_win_steps)} order rate: {m_first/(test_episodes-m_first)}")
    print(f"minimax 2 winning times: {battle_win_N}   average steps: {np.mean(battle_win_steps)} order rate:{b_first/(test_episodes-b_first)}")


