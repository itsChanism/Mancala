#!/usr/bin/env python3
"""
Mancala Controller for CSC 242 Spring 2025
(Written by o3-mini-high and AP.)
(Bugfix for PIE rule by Ethan Mentzer)

This elegant and efficient Python program acts as a controller between two
external player programs. It uses plain text messaging over standard IO.
Every message from the controller is a single line of the form:

  STATE <N> <p11> ... <p1N> <p21> ... <p2N> <p1S> <p2S> <turn> <player>

where:
  - <N> is the number of pits per player (default 6),
  - <pij> are the seed counts in each pit,
  - <p1S>, <p2S> are the stores,
  - <turn> is the ply count, and
  - <player> is the current player’s id (1 or 2).

Players respond by outputting one line:
  - Either an integer 1–N (sowing the seeds from that pit)
  - Or, if it’s player 2’s first turn, the string "PIE" (to invoke the pie rule).

The controller verifies legality, updates state (including extra moves
and captures), and (if “PIE” is called) swaps the board and the players.
"""

import sys, subprocess, argparse, shlex

class MancalaState:
    __slots__ = ('N', 'board', 'turn', 'current_player', 'pie_rule_available')

    # One approach would be to have the entire board (including pits) be a single array.
    # We have chosen this, and use an internal representation slightly different from the printed one.
    # Note that the player 1 store is in the middle of this list, vs toward the end.
    

    def __init__(self, pits, seeds_per_pit=4):
        self.N = pits
        # Board layout:
        # indices 0..N-1: Player 1 pits
        # index N: player 1 store
        # indices N..2*N-1: Player 2 pits
        # index 2*N+1: player 2 store
        self.board = ([seeds_per_pit] * pits + [0] +
                      [seeds_per_pit] * pits + [0])
        self.turn = 1           # ply count (each move counts)
        self.current_player = 1 # either 1 or 2
        # When player 2’s first move is pending, they may opt for “PIE.”
        self.pie_rule_available = True

    def get_state_str(self):
        """Return a string representation of the game state.
        Note that the assignment specifies both stores listed after all pits,
        but this implementation uses a different ordering internally for efficiency.
        We use the format matching the assingnment specs in all IO."""
        parts = ["STATE", str(self.N)]
        # Player 1 pits:
        parts.extend(str(x) for x in self.board[0:self.N])
        # Player 2 pits:
        parts.extend(str(x) for x in self.board[self.N+1:2*self.N+1])
        # Stores:
        parts.append(str(self.board[self.N]))
        parts.append(str(self.board[2*self.N+1]))
        # Turn count and current player:
        parts.append(str(self.turn))
        parts.append(str(self.current_player))
        return " ".join(parts)

    def game_over(self):
        """Game is over when one side’s pits are all empty."""
        side1_empty = all(x == 0 for x in self.board[0:self.N])
        side2_empty = all(x == 0 for x in self.board[self.N+1:2*self.N+1])
        return side1_empty or side2_empty

    def collect_remaining(self):
        """At game end, collect remaining seeds into the appropriate store."""
        # One of the sides must sum to zero, so it should be safe to do it for both.
        side1 = sum(self.board[0:self.N])
        side2 = sum(self.board[self.N+1:2*self.N+1])
        for i in range(self.N):
            self.board[i] = 0
        for i in range(self.N+1, 2*self.N+1):
            self.board[i] = 0
        self.board[self.N] += side1
        self.board[2*self.N+1] += side2

    def apply_move(self, move):
        """
        Apply the move given by the current player.
        move: a string containing either an integer (pit number) or "PIE"
        
        Returns True if the move earns an extra turn (so the same player continues),
        False if play should switch.
        
        Raises ValueError if the move is illegal.
        """
        move = move.strip().upper()
        # --- Handle the pie rule:
        if move == "PIE":
            if self.current_player != 2 or not self.pie_rule_available:
                raise ValueError("PIE move not allowed now")
            # Swap board halves: exchange the pits and stores.
            for i in range(self.N):
                self.board[i], self.board[1+self.N+i] = self.board[1+self.N+i], self.board[i]
            self.board[self.N], self.board[2*self.N+1] = self.board[2*self.N+1], self.board[self.N]
            # Mark that PIE is no longer available.
            self.pie_rule_available = False
            self.current_player = 1 if self.current_player == 2 else 1
            self.turn += 1
            return True

        # --- Otherwise, the move should be an integer pit number.
        try:
            pit_number = int(move)
        except ValueError:
            raise ValueError("Move must be an integer (or PIE)")

        if not (1 <= pit_number <= self.N):
            raise ValueError("Pit number out of range")

        # Map the player's pit choice (1-indexed) to a global board index.
        if self.current_player == 1:
            pos = pit_number - 1
        else:
            pos = self.N + pit_number
            # Once a normal (sown) move has been made by player2, player 2 loses the option to invoke PIE.
            self.pie_rule_available = False
            

        if self.board[pos] == 0:
            raise ValueError("Chosen pit is empty")

        # Pick up the seeds:
        seeds = self.board[pos]
        self.board[pos] = 0
        total_positions = 2*self.N + 2

        # Sow seeds counter-clockwise:
        while seeds > 0:
            pos  = (1 + pos) % total_positions
            # Skip the opponent’s store:
            if ((self.current_player == 2 and pos == self.N) or
                (self.current_player == 1 and pos == 2 * self.N+1)):
                continue
            self.board[pos] += 1
            seeds -= 1

        # Determine if an extra turn is earned:
        if self.current_player == 1 and pos == self.N:
            extra_turn = True
        elif self.current_player == 2 and pos == 2*self.N+1:
            extra_turn = True
        else:
            extra_turn = False

        # --- Check capture rule:
        # If the last seed lands in an empty pit on the mover's own side,
        # capture that seed plus any seeds in the opposite pit.
        captured = 0
        if self.current_player == 1 and 0 <= pos < self.N and self.board[pos] == 1:
            opp = 2*self.N - pos
            if self.board[opp] > 0:
                captured = self.board[opp] + self.board[pos]
                self.board[self.N] += captured
                self.board[opp] = 0
                self.board[pos] = 0
        elif self.current_player == 2 and self.N+1 <= pos < 2*self.N+1 and self.board[pos] == 1:
            opp = 2*self.N - pos
            if self.board[opp] > 0:
                captured = self.board[opp] + self.board[pos]
                self.board[2*self.N+1] += captured
                self.board[opp] = 0
                self.board[pos] = 0

        if captured > 0:
            print(f'Player {self.current_player} captures {captured} stones!')                
        self.turn += 1
        if not extra_turn:
            self.current_player = 1 if self.current_player == 2 else 2
        
        return extra_turn

    def get_scores(self):
        return self.board[self.N], self.board[2*self.N+1]

    
def main():
    parser = argparse.ArgumentParser(
        description="Mancala Controller (communicates via standard IO).")
    parser.add_argument("--player1", required=True,
                        help="Command line (quoted) for player1")
    parser.add_argument("--player2", required=True,
                        help="Command line (quoted) for player2")
    parser.add_argument("--pits", type=int, default=6,
                        help="Number of pits per player (default: 6)")
    parser.add_argument("--seeds", type=int, default=4,
                        help="Initial seeds per pit (default: 4)")
    parser.add_argument("--debug", default=False, action="store_true",
                        help="Print extra information from the controller to console.")
    args = parser.parse_args()

    N = args.pits
    seeds = args.seeds

    # Start the two external player processes.
    # The shlex package works for splitting by argument, vs by whitespace.
    p1_cmd = shlex.split(args.player1)
    p2_cmd = shlex.split(args.player2)

    game = MancalaState(N, seeds)

    # Main game loop.
    while not game.game_over():        
        cur = game.current_player
        state_msg = game.get_state_str()
        # Send the state message to the current player's stdin.
        try:
            if cur == 1:
                proc = subprocess.Popen(p1_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            elif cur == 2:
                proc = subprocess.Popen(p2_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            else:
                raise ValueError("Invalid player identifier: " + str(cur))
        except Exception as e:
            print("Error starting player processes:", e)
            sys.exit(1)
        try:
            if args.debug:
                print(f'Sending {state_msg} to player {game.current_player}')
            proc.stdin.write(state_msg + "\n")
            proc.stdin.flush()
            proc.stdin.close()
        except Exception as e:
            print(f"Error writing to player {cur}: {e}")
            sys.exit(1)

        move = None
        try:
            # Read the move (a single line) from the current player.
            move = proc.stdout.readline()
            proc.terminate()
        except Exception as e:
            print("Exception: ", e)
        if not move:
            winner = 1 if cur == 2 else 2
            print(f"Player {cur} did not respond; Player {winner} wins by default!")
            print(f"WIN {winner}")            
            sys.exit(0)
            
        move = move.strip()
        print(f"Turn {game.turn}, Player {cur} move: {move}")
        # Apply the move. An illegal move ends the game.
        try:
            game.apply_move(move)
        except ValueError as e:
            print(f"Illegal move by player {cur}: {e}")
            winner = 1 if cur == 2 else 2
            print(f"Player {winner} wins by default!")
            print(f"WIN {winner}")            
            sys.exit(0)

        

    # Game over: collect remaining seeds and report the final score.
    game.collect_remaining()
    p1_score, p2_score = game.get_scores()
    print("Game Over")
    print(f"Final Scores: Player 1: {p1_score}, Player 2: {p2_score}")
    if p1_score > p2_score:
        print("Player 1 wins!")
        print("WIN 1")            
    elif p2_score > p1_score:
        print("Player 2 wins!")
        print("WIN 2")
    else:
        print("It's a tie!")
        print("DRAW")
    sys.exit(0)

if __name__ == "__main__":
    main()
