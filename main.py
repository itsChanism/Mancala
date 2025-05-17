# Jiamu Tang 
# jtang41@u.rochester.edu
# personal work no teammate

import copy
import sys
import time


class GameState:
    def __init__(self, p1_pits, p2_pits, p1_store, p2_store, turn, current_player):
        self.p1_pits = p1_pits.copy()
        self.p2_pits = p2_pits.copy()
        self.p1_store = p1_store
        self.p2_store = p2_store
        self.turn = turn
        self.current_player = current_player

    def is_terminal(self):
        return all(count == 0 for count in self.p1_pits) or all(count == 0 for count in self.p2_pits)

    def get_legal_moves(self):
        moves = []
        # legal PIE move on Player 2's first turn.
        if self.current_player == 2 and self.turn == 2:
            moves.append("PIE")
        pits = self.p1_pits if self.current_player == 1 else self.p2_pits
        for i in range(6):
            if pits[i] > 0:
                moves.append(i + 1)
        return moves

    def apply_move(self, move):
        new_state = copy.deepcopy(self)
        if move == "PIE":
            new_state.p1_pits, new_state.p2_pits = new_state.p2_pits, new_state.p1_pits
            new_state.p1_store, new_state.p2_store = new_state.p2_store, new_state.p1_store
            new_state.current_player = 1
            new_state.turn += 1
            return new_state

        pit_index = move - 1
        current_pits = new_state.p1_pits if new_state.current_player == 1 else new_state.p2_pits
        opponent_pits = new_state.p2_pits if new_state.current_player == 1 else new_state.p1_pits
        stones = current_pits[pit_index]
        if stones == 0:
            return self  # illegal move, return unchanged state

        current_pits[pit_index] = 0
        current_pos = pit_index + 1
        # mapping: positions 0-5: current player's pits, position 6: store,
        # positions 7-12: opponent's pits (mirrored).
        while stones > 0:
            if current_pos < 6:
                current_pits[current_pos] += 1
            elif current_pos == 6:
                if new_state.current_player == 1:
                    new_state.p1_store += 1
                else:
                    new_state.p2_store += 1
            else:
                opponent_pos = 12 - current_pos
                if 0 <= opponent_pos < 6:
                    opponent_pits[opponent_pos] += 1
            current_pos = (current_pos + 1) % 13
            stones -= 1

        last_pos = (current_pos - 1) % 13
        # this is extra turn if last seed lands in player's store (position 6).
        another_turn = (last_pos == 6)
        # Capture: if last stone lands in an empty pit on player's side (and no extra turn)
        if 0 <= last_pos < 6 and current_pits[last_pos] == 1 and not another_turn:
            opponent_pos = 5 - last_pos
            if opponent_pits[opponent_pos] > 0:
                if new_state.current_player == 1:
                    new_state.p1_store += 1 + opponent_pits[opponent_pos]
                else:
                    new_state.p2_store += 1 + opponent_pits[opponent_pos]
                current_pits[last_pos] = 0
                opponent_pits[opponent_pos] = 0

        new_state.turn += 1
        new_state.current_player = self.current_player if another_turn else (1 if self.current_player == 2 else 2)
        # game end, collect remaining stones.
        if new_state.is_terminal():
            new_state.p1_store += sum(new_state.p1_pits)
            new_state.p2_store += sum(new_state.p2_pits)
            new_state.p1_pits = [0] * 6
            new_state.p2_pits = [0] * 6

        return new_state

def evaluate(state, maximizing_player):
    # Terminal evaluation: return a high score if winning, low if losing. i should be righ！！！！！
    if state.is_terminal():
        if maximizing_player == 1:
            return (state.p1_store - state.p2_store) * 10000
        else:
            return (state.p2_store - state.p1_store) * 10000

    if maximizing_player == 1:
        store_diff = state.p1_store - state.p2_store
        pit_diff = sum(state.p1_pits) - sum(state.p2_pits)
    else:
        store_diff = state.p2_store - state.p1_store
        pit_diff = sum(state.p2_pits) - sum(state.p1_pits)

    mobility = len(state.get_legal_moves())

    #potential: count opportunities for a capture.
    capture_potential = 0
    if maximizing_player == 1:
        for i in range(6):
            if state.p1_pits[i] == 0 and state.p2_pits[5 - i] > 0:
                capture_potential += 1
    else:
        for i in range(6):
            if state.p2_pits[i] == 0 and state.p1_pits[5 - i] > 0:
                capture_potential += 1

    # this should be bonus for extra round
    pits_to_check = state.p1_pits if maximizing_player == 1 else state.p2_pits
    extra_turn_bonus = 10 if any(
        state.apply_move(i + 1).current_player == maximizing_player
        for i in range(6) if pits_to_check[i] > 0
    ) else 0

    score = store_diff * 10 + pit_diff * 2 + mobility * 2 + capture_potential * 3 + extra_turn_bonus
    return score

def minimax(state, depth, alpha, beta, maximizing_player, start_time, time_limit):
    if depth == 0 or state.is_terminal() or time.time() - start_time >= time_limit:
        return evaluate(state, maximizing_player)
    
    legal_moves = state.get_legal_moves()
    if not legal_moves:
        return evaluate(state, maximizing_player)
    
    if state.current_player == maximizing_player:
        max_val = -float('inf')
        for move in legal_moves:
            if time.time() - start_time >= time_limit:
                break
            child = state.apply_move(move)
            val = minimax(child, depth - 1, alpha, beta, maximizing_player, start_time, time_limit)
            max_val = max(max_val, val)
            alpha = max(alpha, val)
            if beta <= alpha:
                break
        return max_val
    else:
        min_val = float('inf')
        for move in legal_moves:
            if time.time() - start_time >= time_limit:
                break
            child = state.apply_move(move)
            val = minimax(child, depth - 1, alpha, beta, maximizing_player, start_time, time_limit)
            min_val = min(min_val, val)
            beta = min(beta, val)
            if beta <= alpha:
                break
        return min_val

def get_best_move(state, time_limit):
    start_time = time.time()
    legal_moves = state.get_legal_moves()
    # there are fallback in alpha beta test, avoid
    fallback_move = legal_moves[0] if legal_moves else None
    best_move = fallback_move
    best_val = -float('inf')
    
    # PIEEE< If PIE is available, consider it first.
    if "PIE" in legal_moves:
        pie_state = state.apply_move("PIE")
        pie_value = evaluate(pie_state, state.current_player)
        best_val, best_move = pie_value, "PIE"
    
    current_depth = 1
    # Allow a small buffer (0.01 seconds) to ensure a move is returned before the time limit.
    while time.time() - start_time < time_limit - 0.01:
        for move in legal_moves:
            if move == "PIE":
                continue
            child = state.apply_move(move)
            val = minimax(child, current_depth, -float('inf'), float('inf'), state.current_player, start_time, time_limit)
            if val > best_val:
                best_val, best_move = val, move
        current_depth += 1
    if best_move is None:
        best_move = fallback_move
    return best_move

def main():
    input_line = sys.stdin.readline().strip()
    parts = input_line.split()
    state = GameState(
        list(map(int, parts[2:8])),
        list(map(int, parts[8:14])),
        int(parts[14]),
        int(parts[15]),
        int(parts[16]),
        int(parts[17])
    )
    print(get_best_move(state, 0.95))

if __name__ == "__main__":
    main()
