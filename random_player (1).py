# A mancala player that returns random - valid - moves.
# This program should return ONE move based on ONE line of state.

import argparse
import random
import sys
from datetime import datetime

def main():
    parser = argparse.ArgumentParser("A mancala player which randomly selects valid moves.")
    parser.add_argument('--debug', default=False, action='store_true')
    args = parser.parse_args()
                        

    random.seed(datetime.now().timestamp())

    state = input()
    N = int(state.split()[1])
    p1_pits = [int(x) for x in  state.split()[2:2+N]]
    p2_pits = [int(x) for x in  state.split()[2+N:2+2*N]]
    p1_store = int(state.split()[2 + 2 * N])
    p2_store = int(state.split()[3 + 2 * N])
    turn = int(state.split()[-2])
    player = state.split()[-1]
    
    if args.debug:
        sys.stderr.write(f'raw state input: {state}\n')
        sys.stderr.write(f'p1_pits: {p1_pits}, p2_pits {p2_pits}, p1_store: {p1_store}, p2_store {p2_store}, turn: {turn}, player: {player}\n')
    # Valid options if turn == 2 PIE is valid.
    # In either case, any non-empty pit is a valid move.

    #  Diagram:
    #  p1S p11 p12 ... p1N
    #      p21 p22 ... p2N p2S
    
    valid = []
    if turn == 2 and player == '2':
        valid.append('PIE')
        
    if player == '1':
        # check p1 slots        
        for k in range(N):
            if p1_pits[k] > 0:
                valid.append(k+1)
    else:
        # check p2 slots
        for k in range(N):
            if p2_pits[k] > 0:
                valid.append(k+1)

    # randomly choose

    print(random.choice(valid))
        
    
if __name__ == '__main__':
    main()
