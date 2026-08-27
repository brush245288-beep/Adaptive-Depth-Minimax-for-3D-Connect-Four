import math
import random,pickle,time
BOARD_SIZE = 4

depth_time = {}

def load_mdict_table(path="minimax_dict.pkl"):
    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return {}

minimax_dict_test = {}
#------------Underlying logic------------
def win(p1, p2, player):
    board = p1 if player == 1 else p2
    for mask in line_masks:
        if board & mask == mask:
            return True
    return False
def draw(p1, p2, player):
    board = p1 | p2
    full_number = 2 ** 64 -1
    if board == full_number and win(p1, p2, player) == False:
        return True
    return False

def gravity_engining_bit(p1, p2, y, x):
    bit_board = p1 | p2
    for z in range(BOARD_SIZE):
        position = z * 16 + 4 * y + x
        mask = 1 << position
        if bit_board & mask == 0:
            return position
    return None
def z_blades():

    z_blades = []

    # z line
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            mask = 0
            for z in range(BOARD_SIZE):
                index = z * 16 + y * 4 + x
                mask |= (1 << index)
            z_blades.append(mask)
    return z_blades
def line_mask():
    line_mask = []

    #x line
    for z in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            mask = 0
            for x in range(BOARD_SIZE):
                index = z * 16 + y * 4 + x
                mask |= (1 << index)
            line_mask.append(mask)
    #y line
    for z in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            mask = 0
            for y in range(BOARD_SIZE):
                index = z * 16 + y * 4 + x
                mask |= (1 << index)
            line_mask.append(mask)
    #z line
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            mask = 0
            for z in range(BOARD_SIZE):
                index = z * 16 + y * 4 + x
                mask |= (1 << index)
            line_mask.append(mask)
    #xy diag
    for z in range(BOARD_SIZE):
        mask = 0
        for i in range(BOARD_SIZE):
            index = z * 16 + i * 4 + i
            mask |= (1 << index)
        line_mask.append(mask)

    for z in range(BOARD_SIZE):
        mask = 0
        for i in range(BOARD_SIZE):
            index = z * 16 + (3-i) * 4 + i
            mask |= (1 << index)
        line_mask.append(mask)
    #zy
    for x in range(BOARD_SIZE):
        mask = 0
        for i in range(BOARD_SIZE):
            index = i * 16 + i * 4 + x
            mask |= (1 << index)
        line_mask.append(mask)
    for x in range(BOARD_SIZE):
        mask = 0
        for i in range(BOARD_SIZE):
            index = (3-i) * 16 + i * 4 + x
            mask |= (1 << index)
        line_mask.append(mask)
    #zx
    for y in range(BOARD_SIZE):
        mask = 0
        for i in range(BOARD_SIZE):
            index = i * 16 + y * 4 + i
            mask |= (1 << index)
        line_mask.append(mask)
    for y in range(BOARD_SIZE):
        mask = 0
        for i in range(BOARD_SIZE):
            index = (3-i) * 16 + y * 4 + i
            mask |= (1 << index)
        line_mask.append(mask)
    #space diag
    mask = 0
    for i in range(BOARD_SIZE):
        index = i * 16 + i * 4 + i
        mask |= (1 << index)
    line_mask.append(mask)
    mask = 0
    for i in range(BOARD_SIZE):
        index = (3-i) * 16 + i * 4 + i
        mask |= (1 << index)
    line_mask.append(mask)
    mask = 0
    for i in range(BOARD_SIZE):
        index = i * 16 + i * 4 + (3-i)
        mask |= (1 << index)
    line_mask.append(mask)
    mask = 0
    for i in range(BOARD_SIZE):
        index = (3-i) * 16 + i * 4 + (3-i)
        mask |= (1 << index)
    line_mask.append(mask)

    return line_mask

line_masks = line_mask()
z_blade = z_blades()
def play_position(p1, p2, player, position):
    if player == 1:
        return p1 | (1 << position), p2
    return p1, p2 | (1 << position)

def other_player(player):
    return 2 if player == 1 else 1

#--------------bit encode---------------
def encode_board(board):
    player1 = 1
    player2 = 2

    player1_board = 0
    player2_board = 0
    position = -1
    for z in range(BOARD_SIZE - 1, -1, -1):
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                position += 1
                if board[z, y, x] == player1:
                    player1_board |= 1 << position
                if board[z, y, x] == player2:
                    player2_board |= 1 << position
    return player1_board, player2_board

def decode_coordinates(position):
    z = 3 - position // 16
    layer_position = position % 16
    y = layer_position // 4
    x = layer_position % 4
    return z, y, x

def encode_normalized_board(player1_board,player2_board):
    # ==========flip left and right (horizontal)==========
    #1100 -> 0011
    # p1
    flipped_row_p1_H = 0
    for i in range(BOARD_SIZE*BOARD_SIZE):
        row = (player1_board >> (i * BOARD_SIZE)) & 0b1111
        flipped_row_bit1 = ((row & 1) << 3) | (row & 2) << 1 | (row & 4) >> 1 | ((row & 8) >> 3)
        flipped_row_p1_H |= (flipped_row_bit1 << i * BOARD_SIZE)
    #p2
    flipped_row_p2_H = 0
    for i in range(BOARD_SIZE*BOARD_SIZE):
        row = (player2_board >> (i * BOARD_SIZE)) & 0b1111
        flipped_row_bit2 = ((row & 1) << 3) | (row & 2) << 1 | (row & 4) >> 1 | ((row & 8) >> 3)
        flipped_row_p2_H |= (flipped_row_bit2 << i * BOARD_SIZE)

    # ==========flip top and bottom (vertical)==========
    ''' 
        1 0 1 0              0 0 0 0
        0 0 0 0    ----->    0 1 0 1
        0 1 0 1              0 0 0 0
        0 0 0 0              1 0 1 0
    '''
    # p1
    flipped_row_p1_V = 0
    for i in range(BOARD_SIZE):
        layer = (player1_board >> (i * BOARD_SIZE * BOARD_SIZE)) & 0b1111111111111111
        layer_flipped_bit1 = ((layer & 0b1111) << 12) | ((layer & 0b11110000) << 4) | ((layer & 0b111100000000) >> 4) | ((layer & 0b1111000000000000) >> 12)
        flipped_row_p1_V |= (layer_flipped_bit1 << (i * BOARD_SIZE * BOARD_SIZE))
    #p2
    flipped_row_p2_V = 0
    for i in range(BOARD_SIZE):
        layer = (player2_board >> (i * BOARD_SIZE * BOARD_SIZE)) & 0b1111111111111111
        layer_flipped_bit2 = ((layer & 0b1111) << 12) | ((layer & 0b11110000) << 4) | ((layer & 0b111100000000) >> 4) | ((layer & 0b1111000000000000) >> 12)
        flipped_row_p2_V |= (layer_flipped_bit2 << (i * BOARD_SIZE * BOARD_SIZE))
    # =============flip main dig=================
    # p1
    diag_flipped_p1 = 0
    for i in range(BOARD_SIZE):
        layer = (player1_board >> (i * BOARD_SIZE * BOARD_SIZE)) & 0b1111111111111111
        diag_p1 = layer & 0b1000010000100001
        layer_diag_flipped_p1 = ((layer &  0b100001000010) << 3) | ((layer & 0b10000100) << 6) | ((layer & 0b1000) << 9) | ((layer & 0b100001000010000) >> 3) | ((layer & 0b10000100000000) >> 6) | ((layer & 0b1000000000000) >> 9) | diag_p1
        diag_flipped_p1 |= (layer_diag_flipped_p1 << (i * BOARD_SIZE * BOARD_SIZE))
    #p2
    diag_flipped_p2 = 0
    for i in range(BOARD_SIZE):
        layer = (player2_board >> (i * BOARD_SIZE * BOARD_SIZE)) & 0b1111111111111111
        diag_p2 = layer & 0b1000010000100001
        layer_diag_flipped_p2 = ((layer &  0b100001000010) << 3) | ((layer & 0b10000100) << 6) | ((layer & 0b1000) << 9) | ((layer & 0b100001000010000) >> 3) | ((layer & 0b10000100000000) >> 6) | ((layer & 0b1000000000000) >> 9) | diag_p2
        diag_flipped_p2 |= (layer_diag_flipped_p2 << (i * BOARD_SIZE * BOARD_SIZE))

    # =================flip inv dig==================
    #p1
    inv_diag_flipped_p1 = 0
    for i in range(BOARD_SIZE):
        layer = (player1_board >> (i * BOARD_SIZE * BOARD_SIZE)) & 0b1111111111111111
        inv_diag_p1 = layer & 0b1001001001000
        layer_inv_diag_flipped_p1 = ((layer & 0b100100100) << 5) | ((layer & 0b10010) << 10) | ((layer & 1) << 15) | ((layer & 0b10010010000000) >> 5) | ((layer & 0b100100000000000) >> 10) | ((layer & 0b1000000000000000) >> 15) | inv_diag_p1
        inv_diag_flipped_p1 |= (layer_inv_diag_flipped_p1 << (i * BOARD_SIZE *BOARD_SIZE))
    #p2
    inv_diag_flipped_p2 = 0
    for i in range(BOARD_SIZE):
        layer = (player2_board >> (i * BOARD_SIZE * BOARD_SIZE)) & 0b1111111111111111
        inv_diag_p2 = layer & 0b1001001001000
        layer_inv_diag_flipped_p2 = ((layer & 0b100100100) << 5) | ((layer & 0b10010) << 10) | ((layer & 1) << 15) | (
                    (layer & 0b10010010000000) >> 5) | ((layer & 0b100100000000000) >> 10) | (
                                                (layer & 0b1000000000000000) >> 15) | inv_diag_p2
        inv_diag_flipped_p2 |= (layer_inv_diag_flipped_p2 << (i * BOARD_SIZE * BOARD_SIZE))

    # ===============rotate 90=========================
    #p1
    rot_90_p1 = 0
    for i in range(BOARD_SIZE):
        layer = (player1_board >> (i * BOARD_SIZE * BOARD_SIZE)) & 0b1111111111111111
        c1 = (layer & 1) | ((layer & 0b10000) >> 3) | ((layer & 0b100000000) >> 6) | ((layer & 0b1000000000000) >> 9)
        c2 = ((layer & 2) >> 1) | ((layer & 0b100000) >> 4) | ((layer & 0b1000000000) >> 7) | ((layer &0b10000000000000) >> 10)
        c3 = ((layer & 4) >> 2) | ((layer & 0b1000000) >> 5) | ((layer & 0b10000000000) >> 8) | ((layer & 0b100000000000000) >> 11)
        c4 = ((layer & 8) >> 3) | ((layer & 0b10000000) >> 6) | ((layer & 0b100000000000) >> 9) | ((layer & 0b1000000000000000) >> 12)
        rot_layer1 = c4 | (c3 << 4) | (c2 << 8) | (c1 << 12)
        rot_90_p1 |= (rot_layer1 << (i * BOARD_SIZE * BOARD_SIZE))
    #p2
    rot_90_p2 = 0
    for i in range(BOARD_SIZE):
        layer = (player2_board >> (i * BOARD_SIZE * BOARD_SIZE)) & 0b1111111111111111
        c1 = (layer & 1) | ((layer & 0b10000) >> 3) | ((layer & 0b100000000) >> 6) | ((layer & 0b1000000000000) >> 9)
        c2 = ((layer & 2) >> 1) | ((layer & 0b100000) >> 4) | ((layer & 0b1000000000) >> 7) | (
                    (layer & 0b10000000000000) >> 10)
        c3 = ((layer & 4) >> 2) | ((layer & 0b1000000) >> 5) | ((layer & 0b10000000000) >> 8) | (
                    (layer & 0b100000000000000) >> 11)
        c4 = ((layer & 8) >> 3) | ((layer & 0b10000000) >> 6) | ((layer & 0b100000000000) >> 9) | (
                    (layer & 0b1000000000000000) >> 12)
        rot_layer2 = c4 | (c3 << 4) | (c2 << 8) | (c1 << 12)
        rot_90_p2 |= (rot_layer2 << (i * BOARD_SIZE * BOARD_SIZE))

    # ===================rotate 180====================
    # p1
    rot_180_p1 = 0
    for i in range(BOARD_SIZE):
        layer = (player1_board >> (i * BOARD_SIZE * BOARD_SIZE)) & 0b1111111111111111
        row1 = layer & 0b1111
        row2 = (layer & 0b11110000) >> 4
        row3 = (layer & 0b111100000000) >> 8
        row4 = (layer & 0b1111000000000000) >> 12

        row1_flipped = ((row1 & 1) << 3) | ((row1 & 2) << 1) | ((row1 & 4) >> 1) | ((row1 & 8) >> 3)
        row2_flipped = ((row2 & 1) << 3) | ((row2 & 2) << 1) | ((row2 & 4) >> 1) | ((row2 & 8) >> 3)
        row3_flipped = ((row3 & 1) << 3) | ((row3 & 2) << 1) | ((row3 & 4) >> 1) | ((row3 & 8) >> 3)
        row4_flipped = ((row4 & 1) << 3) | ((row4 & 2) << 1) | ((row4 & 4) >> 1) | ((row4 & 8) >> 3)

        rot_layer1 = row4_flipped | (row3_flipped << 4) | (row2_flipped << 8) | (row1_flipped << 12)
        rot_180_p1 |= (rot_layer1 << (i * BOARD_SIZE * BOARD_SIZE))
    # p2
    rot_180_p2 = 0
    for i in range(BOARD_SIZE):
        layer = (player2_board >> (i * BOARD_SIZE * BOARD_SIZE)) & 0b1111111111111111
        row1 = layer & 0b1111
        row2 = (layer & 0b11110000) >> 4
        row3 = (layer & 0b111100000000) >> 8
        row4 = (layer & 0b1111000000000000) >> 12

        row1_flipped = ((row1 & 1) << 3) | ((row1 & 2) << 1) | ((row1 & 4) >> 1) | ((row1 & 8) >> 3)
        row2_flipped = ((row2 & 1) << 3) | ((row2 & 2) << 1) | ((row2 & 4) >> 1) | ((row2 & 8) >> 3)
        row3_flipped = ((row3 & 1) << 3) | ((row3 & 2) << 1) | ((row3 & 4) >> 1) | ((row3 & 8) >> 3)
        row4_flipped = ((row4 & 1) << 3) | ((row4 & 2) << 1) | ((row4 & 4) >> 1) | ((row4 & 8) >> 3)

        rot_layer2 = row4_flipped | (row3_flipped << 4) | (row2_flipped << 8) | (row1_flipped << 12)
        rot_180_p2 |= (rot_layer2 << (i * BOARD_SIZE * BOARD_SIZE))

    # ===================rotate 270===================
    # p1
    rot_270_p1 = 0
    for i in range(BOARD_SIZE):
        layer = (player1_board >> (i * BOARD_SIZE * BOARD_SIZE)) & 0b1111111111111111
        c1 = ((layer & 1) << 3) | ((layer & 0b10000) >> 2) | ((layer & 0b100000000) >> 7) | ((layer & 0b1000000000000) >> 12)
        c2 = ((layer & 2) << 2) | ((layer & 0b100000) >> 3) | ((layer & 0b1000000000) >> 8) | ((layer & 0b10000000000000) >> 13)
        c3 = ((layer & 4) << 1) | ((layer & 0b1000000) >> 4) | ((layer & 0b10000000000) >> 9) | ((layer & 0b100000000000000) >> 14)
        c4 = (layer & 8) | ((layer & 0b10000000) >> 5) | ((layer & 0b100000000000) >> 10) | ((layer & 0b1000000000000000) >> 15)
        rot_layer1 = c1 | (c2 << 4) | (c3 << 8) | (c4 << 12)
        rot_270_p1 |= (rot_layer1 << (i * BOARD_SIZE * BOARD_SIZE))
    # p2
    rot_270_p2 = 0
    for i in range(BOARD_SIZE):
        layer = (player2_board >> (i * BOARD_SIZE * BOARD_SIZE)) & 0b1111111111111111
        c1 = ((layer & 1) << 3) | ((layer & 0b10000) >> 2) | ((layer & 0b100000000) >> 7) | ((layer & 0b1000000000000) >> 12)
        c2 = ((layer & 2) << 2) | ((layer & 0b100000) >> 3) | ((layer & 0b1000000000) >> 8) | ((layer & 0b10000000000000) >> 13)
        c3 = ((layer & 4) << 1) | ((layer & 0b1000000) >> 4) | ((layer & 0b10000000000) >> 9) | ((layer & 0b100000000000000) >> 14)
        c4 = (layer & 8) | ((layer & 0b10000000) >> 5) | ((layer & 0b100000000000) >> 10) | ((layer & 0b1000000000000000) >> 15)
        rot_layer2 = c1 | (c2 << 4) | (c3 << 8) | (c4 << 12)
        rot_270_p2 |= (rot_layer2 << (i * BOARD_SIZE * BOARD_SIZE))

    normalized_candidates = [
        (player1_board, player2_board),
        (flipped_row_p1_H, flipped_row_p2_H),
        (flipped_row_p1_V, flipped_row_p2_V),
        (diag_flipped_p1, diag_flipped_p2),
        (inv_diag_flipped_p1, inv_diag_flipped_p2),
        (rot_90_p1, rot_90_p2),
        (rot_180_p1, rot_180_p2),
        (rot_270_p1, rot_270_p2),
    ]

    return min(normalized_candidates)




def board_full(p1,p2):
    total = p1.bit_count() + p2.bit_count()
    if total == 64:
        return True
    return False
#---------------------minimax relate--------------------------
def get_valid_moves_bit(p1,p2):
    moves = []

    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            position = gravity_engining_bit(p1, p2, y, x)
            if position is not None:
                moves.append(position)
    return moves


def minimax_new_alphabeta_odd(p1, p2, depth, player1, player2, alpha, beta, w_self2, w_self3, w_opp2, w_opp3):
    def evaluation_bin(p1, p2, player, w_self2, w_self3, w_opp2, w_opp3):

        score_p1 = 0
        score_p2 = 0

        def add_line_score(count_p1, count_p2, score_p1, score_p2):

            if count_p2 == 0:
                if count_p1 == 2:
                    score_p1 += w_self2
                elif count_p1 == 3:
                    score_p1 += w_self3


            elif count_p1 == 0:
                if count_p2 == 2:
                    score_p2 += w_opp2
                elif count_p2 == 3:
                    score_p2 += w_opp3

            return score_p1, score_p2

        for mask in line_masks:
            count_p1 = (p1 & mask).bit_count()
            count_p2 = (p2 & mask).bit_count()
            score_p1, score_p2 = add_line_score(count_p1, count_p2, score_p1, score_p2)

        if player == 1:
            return score_p1 - score_p2
        return score_p2 - score_p1

    if win(p1, p2, player2):
        score = 100000 + depth

        return score
    if win(p1, p2, other_player(player2)):
        score = -100000 - depth

        return score
    if draw(p1, p2, player2):
        score = -100000
        # minimax_dict[key] = score
        return score

    if depth == 0:
        return evaluation_bin(p1, p2, player2, w_self2, w_self3, w_opp2, w_opp3)

    moves = get_valid_moves_bit(p1, p2)
    moves.sort(key=lambda position: move_order_score(p1, p2, player1, position), reverse=True)

    if not moves:
        score = evaluation_bin(p1, p2, player2, w_self2, w_self3, w_opp2, w_opp3)
        # minimax_dict[key] = score
        return score

    if player1 == player2:
        best_score = -float("inf")

        for position in moves:
            test_p1, test_p2 = play_position(p1, p2, player1, position)

            score = minimax_new_alphabeta(test_p1, test_p2, depth - 1, other_player(player1), player2, alpha, beta,w_self2, w_self3, w_opp2, w_opp3)
            best_score = max(best_score, score)
            alpha = max(alpha, best_score)

            if alpha >= beta:
                break

        # Store the current board only after all child states have been evaluated.
        # minimax_dict[key] = best_score
        return best_score
    else:
        best_score = float("inf")
        for position in moves:
            test_p1, test_p2 = play_position(p1, p2, player1, position)
            score = minimax_new_alphabeta(test_p1, test_p2, depth - 1, other_player(player1), player2, alpha, beta,w_self2, w_self3, w_opp2, w_opp3)
            best_score = min(best_score, score)
            beta = min(beta, best_score)
            if alpha >= beta:
                break

        # Store the current board only after all child states have been evaluated.
        # minimax_dict[key] = best_score
        return best_score


def evaluation_bin(p1, p2, player, w_self2, w_self3, w_opp2, w_opp3):
    potential3_p1 = []
    potential3_p2 = []
    potential2_p1 = []
    potential2_p2 = []
    mask_win_p1 = []
    mask_win_p2 = []

    w_f3_s = 100
    w_f3_o = 150

    score_p1 = 0
    score_p2 = 0
    if player == 1:
        w_12 = w_self2
        w_13 = w_self3
        w_f1 = w_f3_s
        w_22 = w_opp2
        w_23 = w_opp3
        w_f2 = w_f3_o
        alpha_k1 = 0.2
        alpha_k2 = 1
        wcm_p1 = 700
        wcm_p2 = 1000
    elif player == 2:
        w_22 = w_self2
        w_23 = w_self3
        w_f2 = w_f3_s
        w_12 = w_opp2
        w_13 = w_opp3
        w_f1 = w_f3_o
        alpha_k1 = 1
        alpha_k2 = 0.2
        wcm_p1 = 1000
        wcm_p2 = 700

    def add_line_score(count_p1, count_p2, score_p1, score_p2):
        if count_p2 == 0:
            if count_p1 == 2:
                potential2_p1.append(p1 & mask)
                if (len(potential2_p2)) != 0:
                    score_p1 += w_12 + alpha_k1 * w_12 * (1.1 ** (len(potential2_p1)))
                else:
                    score_p1 += w_12

            elif count_p1 == 3:
                potential3_p1.append(p1 & mask)
                mask_win_p1.append(mask)
                score_p1 += w_13


        elif count_p1 == 0:
            if count_p2 == 2:
                potential2_p2.append(p2 & mask)
                if (len(potential2_p1)) != 0:
                    score_p2 += w_22 + alpha_k2 * w_22 * (1.1 ** (len(potential2_p2)))
                else:
                    score_p2 += w_22
            elif count_p2 == 3:
                potential3_p2.append(p2 & mask)
                mask_win_p2.append(mask)
                score_p2 += w_23

        return score_p1, score_p2

    for mask in line_masks:
        count_p1 = (p1 & mask).bit_count()
        count_p2 = (p2 & mask).bit_count()

        if count_p2 == 0:
            if count_p1 == 2:
                potential2_p1.append(p1 & mask)
            elif count_p1 == 3:
                potential3_p1.append(p1 & mask)

        elif count_p1 == 0:
            if count_p2 == 2:
                potential2_p2.append(p2 & mask)
            elif count_p2 == 3:
                potential3_p2.append(p2 & mask)

    n2_p1 = len(potential2_p1)
    n2_p2 = len(potential2_p2)

    n3_p1 = len(potential3_p1)
    n3_p2 = len(potential3_p2)

    score_p1 = n2_p1 * w_12 + n3_p1 * w_13
    score_p2 = n2_p2 * w_22 + n3_p2 * w_23

    if n2_p2 != 0:
        score_p1 += alpha_k1 * w_12 * sum(1.1 ** k for k in range(1, n2_p1 + 1))

    if n2_p1 != 0:
        score_p2 += alpha_k2 * w_22 * sum(1.1 ** k for k in range(1, n2_p2 + 1))

    board_O = p1 | p2
    score_float_p1 = 0
    score_float_p2 = 0

    for mask in mask_win_p1:
        win_bit = mask & ~board_O
        win_position = win_bit.bit_length() - 1
        float_mask = 0
        for i in range(1, 4):
            float_position = win_position - i * 16
            if float_position < 0:
                break
            float_mask |= (win_bit >> i * 16)

        for z_mask in z_blade:
            if (z_mask & win_bit).bit_count() == 1:
                z_occupy = z_mask
                break
            else:
                z_occupy = 0

        if z_occupy != 0:
            if (z_occupy & board_O) != float_mask:
                score_float_p1 += w_f1

    for mask in mask_win_p2:
        win_bit = mask & ~board_O
        win_position = win_bit.bit_length() - 1
        float_mask = 0
        for i in range(1, 4):
            float_position = win_position - i * 16
            if float_position < 0:
                break
            float_mask |= (win_bit >> i * 16)

        for z_mask in z_blade:
            if (z_mask & win_bit).bit_count() == 1:
                z_occupy = z_mask
                break
            else:
                z_occupy = 0

        if z_occupy != 0:
            if (z_occupy & board_O) != float_mask:
                score_float_p2 += w_f2

    # =======cross mask======

    score_cm1 = 0
    score_cm2 = 0
    # ====p1====
    for i in range(0, len(mask_win_p1) - 1):
        for j in range(1, len(mask_win_p1)):
            c_m = (mask_win_p1[i] & mask_win_p1[j]).bit_count()
            if c_m == 1:
                score_cm1 += wcm_p1
    # ====p2====
    for i in range(0, len(mask_win_p2) - 1):
        for j in range(1, len(mask_win_p2)):
            c_m = (mask_win_p2[i] & mask_win_p2[j]).bit_count()
            if c_m == 1:
                score_cm2 += wcm_p2

    # ----p1p2-----
    score_T = 0
    for i in range(len(mask_win_p1)):
        for j in range(len(mask_win_p2)):
            c_m = (mask_win_p1[i] & mask_win_p2[j]).bit_count()
            if c_m == 1:
                score_T += 500

    # print("score_cm1:", score_cm1, "score_cm2:", score_cm2)
    '''
    if score_T != 0:
        print("score1:", score_p1,"score2:", score_p2)
        print("score_float_p1:", score_float_p1, "score_float_p2:", score_float_p2)
        print("score_cm1:", score_cm1, "score_cm2:", score_cm2)
        print("Score 1: ", score_T, "\n")
    '''
    if player == 1:
        return (score_p1 + score_float_p1 + score_cm1) - (score_p2 + score_float_p2 + score_cm2) + score_T
    return (score_p2 + score_float_p2 + score_cm2) - (score_p1 + score_float_p1 + score_cm1) + score_T


def minimax_new_alphabeta(p1,p2, depth, player1, player2, alpha, beta, w_self2, w_self3, w_opp2, w_opp3,start_time):

    key = (encode_normalized_board(p1,p2), player1, player2)

    entry = minimax_dict_test.get(key)
    if entry is not None and entry["depth"] > depth:
        entry["visits"] += 1
        return entry["score"]

    def lpf_update(new_score):

        if key not in minimax_dict_test:
            minimax_dict_test[key] = {
                "score": new_score,
                "depth": depth,
                "visits": 1
            }
            return minimax_dict_test[key]["score"]

        entry = minimax_dict_test[key]

        if entry["depth"] > depth:
            entry["visits"] += 1
            return entry["score"]

        if entry["depth"] == depth:
            alpha_lpf = 1 / (entry["visits"] + 1)
            entry["score"] = alpha_lpf * new_score + (1 - alpha_lpf) * entry["score"]
            entry["visits"] += 1
            return entry["score"]

        entry["score"] = new_score
        entry["depth"] = depth
        entry["visits"] += 1
        return entry["score"]


    if win(p1,p2, player2):
        score = 100000 + depth
        new_score = lpf_update(score)
        return new_score
    if win(p1,p2, other_player(player2)):
        score = -100000 - depth
        new_score = lpf_update(score)
        return new_score
    if draw(p1,p2, player2):
        score = -100000
        new_score = lpf_update(score)
        return new_score

    if depth == 0:
        return evaluation_bin(p1, p2, player2, w_self2, w_self3, w_opp2, w_opp3)

    moves = get_valid_moves_bit(p1, p2)
    moves.sort(key=lambda position: move_order_score(p1, p2, player1, position), reverse=True)

    if not moves:
        score = evaluation_bin(p1, p2, player2, w_self2, w_self3, w_opp2, w_opp3)
        # minimax_dict[key] = score
        return score

    if player1 == player2:
        best_score = -float("inf")

        for position in moves:
            test_p1, test_p2 = play_position(p1, p2, player1, position)
            score = minimax_new_alphabeta(test_p1,test_p2,depth - 1,other_player(player1),player2,alpha,beta,w_self2,w_self3,w_opp2,w_opp3,start_time)
            best_score = max(best_score, score)
            alpha = max(alpha, best_score)

            if alpha >= beta:
                break


        # Store the current board only after all child states have been evaluated.

        new_score = lpf_update(best_score)
        return new_score
    else:
        best_score = float("inf")
        for position in moves:
            test_p1, test_p2 = play_position(p1, p2, player1, position)
            score = minimax_new_alphabeta(test_p1,test_p2, depth - 1, other_player(player1), player2,alpha,beta,w_self2, w_self3, w_opp2, w_opp3,start_time)
            best_score = min(best_score, score)
            beta = min(beta, best_score)
            if alpha >= beta:
                break



        # Store the current board only after all child states have been evaluated.
        new_score = lpf_update(best_score)
        return new_score


def choose_best_move_dict(p1,p2, player, alpha,beta,w_self2, w_self3, w_opp2, w_opp3, min_depth):
    depths = 22


    def time_control():
        end_time = time.time()
        dt = end_time - start_time
        time_limit = 0.5
        if dt > time_limit:
            print(f"time limit: {time_limit}")
            return False
        return True

    moves = get_valid_moves_bit(p1, p2)
    moves.sort(key=lambda position: move_order_score(p1, p2, player, position), reverse=True)
    start_time = time.time()
    for depth in range(min_depth,depths):
        best_score = -float("inf")
        best_move = None
        for position in moves:

            test_p1, test_p2 = play_position(p1, p2, player, position)

            score = minimax_new_alphabeta(test_p1, test_p2, depth-1, other_player(player), player, alpha, beta, w_self2, w_self3, w_opp2, w_opp3,start_time)
            if score > best_score:
                best_score = score
                best_move = position
        smc_bool = time_control()
        if not smc_bool:
            record_depth = depth
            break
        record_depth = depth

    return best_move, record_depth, 0.5

def potential_connect2(p1,p2, player):

    if player == 1:
        player_bits = p1
        opponent_bits = p2

    else:
        player_bits = p2
        opponent_bits = p1

    num_3_player_bits = 0
    num_3_opponent_bits = 0

    for mask in line_masks:
        count_player = (player_bits & mask).bit_count()
        count_opponent = (opponent_bits & mask).bit_count()
        if count_player == 2 and count_opponent == 0:
            num_3_player_bits += 1
        if count_opponent == 2 and count_player == 0:
            num_3_opponent_bits += 1

    return num_3_player_bits - num_3_opponent_bits

def potential_connect3(p1,p2, player):

    if player == 1:
        player_bits = p1
        opponent_bits = p2

    else:
        player_bits = p2
        opponent_bits = p1

    num_3_player_bits = 0
    num_3_opponent_bits = 0

    for mask in line_masks:
        count_player = (player_bits & mask).bit_count()
        count_opponent = (opponent_bits & mask).bit_count()
        if count_player == 3 and count_opponent == 0:
            num_3_player_bits += 1
        if count_opponent == 3 and count_player == 0:
            num_3_opponent_bits += 1

    return num_3_player_bits - num_3_opponent_bits

def move_order_score(p1, p2, player, position):
    opponent = other_player(player)
    score = 0
    def centre(position):
        z,y,x = decode_coordinates(position)
        if y in (1, 2) and x in (1, 2):
            return 1
        return 0

    def corner(position):
        z,y,x = decode_coordinates(position)
        if z in (0, 3) and y in (0, 3) and x in (0, 3):
            return 1
        return 0
    test_p1, test_p2 = play_position(p1, p2, player, position)
    opp_p1, opp_p2 = play_position(p1,p2,opponent,position)

    if win(test_p1, test_p2, player):
        score += 1000000
    if win(opp_p1, opp_p2, opponent):
        score += 500000

    score_ce = centre(position) * 0.5
    score_p = potential_connect2(test_p1, test_p2, player) * 4
    score_co = corner(position) * 1
    total_score = score_ce + score_p + score + score_co
    noice = random.uniform(-0.02, 0.02) * total_score
    return total_score + noice



#------------------------MCTS------------------------------
node_table = {}

def is_terminal_node(p1, p2):
    return win(p1, p2, 1) or win(p1, p2, 2) or board_full(p1, p2)

def create_node(p1, p2, current_player):
    key = (p1, p2, current_player)

    terminal = is_terminal_node(p1, p2)

    return {
        "key": key,
        "visits": 0,
        "value": 0.0,
        "children": {},          # move -> child_key
        "untried_moves": get_valid_moves_bit(p1, p2),
        "terminal": terminal
    }

def get_node(p1, p2, current_player):

    key = (p1, p2, current_player)

    if key not in node_table:
        node_table[key] = create_node(p1, p2, current_player)

    return node_table[key]

#========select=========
def uct_score(parent_visits, child_visits, child_value, c):

    if child_visits == 0:
        return float("inf")
    exploit = child_value / child_visits
    explore = c * math.sqrt(math.log(parent_visits) / child_visits)
    return exploit + explore

def select_child(node, c=1.414):
    best_move = None
    best_child = None
    best_score = -float("inf")

    for move, child_key in node["children"].items():
        child = node_table[child_key]

        score = uct_score(
            parent_visits=node["visits"],
            child_visits=child["visits"],
            child_value=child["value"],
            c=c,
        )

        if score > best_score:
            best_score = score
            best_move = move
            best_child = child

    return best_move, best_child

def selection(root, c=1.414):
    node = root
    path = [node]

    while not node["terminal"] and not node["untried_moves"]:
        move, node = select_child(node, c)
        path.append(node)

    return node, path

#========expand========

def expand(node):

    if node["terminal"]:
        return node

    if not node["untried_moves"]:
        return node

    p1, p2, current_player = node["key"]
    move_index = random.randrange(len(node["untried_moves"]))
    move = node["untried_moves"].pop(move_index)
    new_p1, new_p2 = play_position(p1, p2, current_player, move)
    next_player = other_player(current_player)
    child = get_node(new_p1, new_p2, next_player)
    node["children"][move] = child["key"]

    return move, child


#=========simulation============

def choose_rollout_move(p1, p2, current_player):
    moves = get_valid_moves_bit(p1, p2)

    for move in moves:
        test_p1, test_p2 = play_position(p1, p2, current_player, move)
        if win(test_p1, test_p2, current_player):
            return move

    opponent = other_player(current_player)
    for move in moves:
        test_p1, test_p2 = play_position(p1, p2, opponent, move)
        if win(test_p1, test_p2, opponent):
            return move

    return random.choice(moves)

def rollout(node, root_player):
    p1, p2, current_player = node["key"]

    while True:
        if win(p1, p2, root_player):
            return 1

        if win(p1, p2, other_player(root_player)):
            return -1

        if board_full(p1, p2):
            return 0

        moves = get_valid_moves_bit(p1, p2)

        if not moves:
            return 0

        move = choose_rollout_move(p1, p2, current_player)
        p1, p2 = play_position(p1, p2, current_player, move)
        current_player = other_player(current_player)

#===============Backpropagation================
def backpropagation(path, result):
    for node in path:
        node["visits"] += 1
        node["value"] += result


#=============main_mct============
import time

def choose_best_move(root):
    best_move = None
    best_visits = -1

    for move, child_key in root["children"].items():
        child = node_table[child_key]

        if child["visits"] > best_visits:
            best_visits = child["visits"]
            best_move = move
    return best_move

def max_tree_depth(root):
    max_depth = 0
    stack = [(root, 0)]

    while stack:
        node, depth = stack.pop()
        max_depth = max(max_depth, depth)

        for child_key in node["children"].values():
            child = node_table[child_key]
            stack.append((child, depth + 1))

    return max_depth

def mcts_search(p1, p2, current_player, time_limit=1.0, return_depth=False):
    root = get_node(p1, p2, current_player)
    root_player = current_player

    end_time = time.time() + time_limit

    while time.time() < end_time:
        leaf, path = selection(root)

        if not leaf["terminal"] and leaf["untried_moves"]:
            move, child = expand(leaf)
            path.append(child)
        else:
            child = leaf

        result = rollout(child, root_player)
        backpropagation(path, result)

    best_move = choose_best_move(root)

    if return_depth:
        return best_move, max_tree_depth(root)

    return best_move

