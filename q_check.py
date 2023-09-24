import pickle
import random
import card_effects2 as ce

MARK_IDS = ce.MARK_IDS
CARD_IDS = ce.CARD_IDS

filename = "q.pkl"
with open(filename, "rb") as f:
	q = pickle.load(f)
	print(f"States in {filename} dict: {len(q)}")

counter = 0 
for key, value in q.items():
	if value != 0:
		counter += 1
print(f"Not zeros: {counter}")

counter = 0
for key, value in q.items():
	if value != 0 and value != 1 and value != -1:
		counter += 1
		if value > 0 and value < 0.4:
			print(value)
		elif value < 0 and value > -0.4:
			print(value)

print(f"Not finals: {counter}")

#for v in random.sample(list(filter(lambda v: v != 0 and v != -1 and v != 1, q.values())), 20):
	#print(v)