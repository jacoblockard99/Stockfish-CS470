#!/usr/bin/env python3

import chess
import chess.engine
import sys
import time
import argparse

# Command-line arguments

parser = argparse.ArgumentParser(
    description="A simple Python program that launches two Stockfish servers with various options and plays them against each other to determine which plays chess better."
)

parser.add_argument("threads1", help="Thread limit for first Stockfish engine.")
parser.add_argument("threads2", help="Thread limit for second Stockfish engine.")
parser.add_argument("stockfish", help="Path to the stockfish executable.")
parser.add_argument("positions", help="Path to a file containing a newline-delimited list of FEN strings representing starting positions. Two games will be run for each position in the file, with each engine getting to go first.")

parser.add_argument("--depth1", help="Limit search depth for first Stockfish engine.", type=int, default=-1)
parser.add_argument("--depth2", help="Limit search depth for second Stockfish engine.", type=int, default=-1)

parser.add_argument("--nodes1", help="Limit nodes searched for first Stockfish engine.", type=int, default=-1)
parser.add_argument("--nodes2", help="Limit nodes searched for second Stockfish engine.", type=int, default=-1)

parser.add_argument("--turn1", help="Limit turn time (s) for first Stockfish engine.", type=float, default=-1)
parser.add_argument("--turn2", help="Limit turn time (s) for second Stockfish engine.", type=float, default=-1)

parser.add_argument("--clock1", help="Limit total clock time (s) for first Stockfish engine.", type=float, default=60)
parser.add_argument("--clock2", help="Limit total clock time (s) for second Stockfish engine.", type=float, default=60)

parser.add_argument("--repeat", help="Repeat all the positions the given number of times.", type=int, default=1)
parser.add_argument("--verbose", help="Print all board positions.", action="store_true")

parser.add_argument("--pos-start", help="Start at the given index (inclusive) in the positions file.", type=int, default=0)
parser.add_argument("--pos-end", help="End at the given index (exclusive) in the positions file.", type=int, default=-1)

args = parser.parse_args()

# Launch the Stockfish servers.

engine1 = chess.engine.SimpleEngine.popen_uci(args.stockfish)
engine1.configure({"Threads": args.threads1})

engine2 = chess.engine.SimpleEngine.popen_uci(args.stockfish)
engine2.configure({"Threads": args.threads2})

# Read the positions file.

with open(args.positions, 'r') as file:
    positions = file.readlines()

if args.pos_end == -1:
    args.pos_end = len(positions)

# Parse the limits given via the command-line.

limits1 = chess.engine.Limit()
if args.depth1 != -1:
    limits1.depth = args.depth1
if args.turn1 != -1:
    limits1.time = args.turn1
if args.nodes1 != -1:
    limits1.nodes = args.nodes1

limits2 = chess.engine.Limit()
if args.depth2 != -1:
    limits2.depth = args.depth2
if args.turn2 != -1:
    limits2.time = args.turn2
if args.nodes2 != -1:
    limits2.nodes = args.nodes2

# Function to simulate a single game between two engines.

def reset_clock():
    limits1.white_clock = args.clock1
    limits1.black_clock = args.clock1
    limits2.white_clock = args.clock2
    limits2.black_clock = args.clock2

def simulate_game(white, black, start_pos, white_limits, black_limits):
    cur = white # current engine
    cur_limits = white_limits # current engine's limits
    board = chess.Board(position)

    # Reset both engines for a new game.
    white.protocol.send_line("ucinewgame")
    black.protocol.send_line("ucinewgame")

    while not board.is_game_over():
        # Play the current player.
        start = time.perf_counter()
        result = cur.play(board, cur_limits)
        end = time.perf_counter()
        board.push(result.move)
        elapsed = end - start
        cur_limits.white_clock -= elapsed
        cur_limits.black_clock -= elapsed
        if cur_limits.white_clock <= 0.001 or cur_limits.black_clock <= 0.001:
            return "black" if cur == white else "white"
        # Toggle player.
        cur = black if cur == white else white
        cur_limits = black_limits if cur_limits == white_limits else white_limits

        if args.verbose:
            print(board, flush=True)
            print("")

    # Figure out result
    if board.result() == "1-0":
        return "white"
    elif board.result() == "0-1":
        return "black"
    else:
        return "draw"

# Run games with all the positions, repeated the requested number of times,
# keeping track of engine 1's wins, engine 2's wins, and draws.

e1wins = 0
e2wins = 0
draws = 0

start = time.perf_counter()
for i in range(args.repeat):
    if args.verbose:
        print(f"Iteration {i}:\n")

    for position in positions[args.pos_start:args.pos_end]:
        # Have engine1 start:
        reset_clock()
        result = simulate_game(engine1, engine2, position, limits1, limits2)
        if result == "white":
            e1wins += 1
        elif result == "black":
            e2wins +=1
        else:
            draws += 1
        # Now have engine2 start:
        reset_clock()
        result = simulate_game(engine2, engine1, position, limits1, limits2)
        if result == "white":
            e2wins += 1
        elif result == "black":
            e1wins +=1
        else:
            draws += 1
end = time.perf_counter()

# Print stats.
print(f"{e1wins} {e2wins} {draws}\n")
print(f"Total: {e1wins + e2wins + draws}\n")
print(f"{end - start:0.6f}")

# Kill the Stockfish servers.
engine1.quit()
engine2.quit()