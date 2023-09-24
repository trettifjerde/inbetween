from game2 import Game
import ai
from card_effects2 import CITY, CREATURE
import sys
import traceback

#q_filename = "q.pkl"

def train(n, filename=None):
	wins = {1: 0, -1: 0}
	IAI = ai.InbetAI(filename)

	for i in range(n):
		g = Game(IAI, humans=0)

		print(f"Training round: {i + 1}...", end=" ")

		g.run_game()
		wins[g.winner] += 1
		IAI.save()

	print(f"CITY: {wins[1]} CREATURE: {wins[-1]}")
	print(f"T-counter: {ai.T_COUNTER}")
	print(f"Q-counter: {ai.Q_COUNTER}")

if __name__ == "__main__":
	train(10)