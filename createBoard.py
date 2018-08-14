import random
import sys

def randomBoard(cols, rows, colorDistribution, seed=None):
	'''
	Taken (and only slightly modified) from https://github.com/Roxxik/SameGame/blob/master/old/core.py

	Generates a random board with `cols` columns and `rows` rows. It has `len(colorDistribution)` with a distribution given in `colorDistribution`. A distribution of `[1, 2, 1]` means that there are as many 2's as there are 1's and 3's.

	:param cols: The number of columns of the board
	:param rows: The number of rows of the board
	:param colorDistribution: List with color distribution as described above
	:param seed: Seed to initialize the pseudo random number generator to get reproducable boards
	:returns: The generated board as a one-line string as described in the competition guidelines
	'''

	colorSum = sum(colorDistribution)
	if seed is not None:
		random.seed(seed)
	coords = [(i, j) for i in range (cols) for j in range (rows)]
	random.shuffle(coords)
	board = [[0 for i in range (cols)] for j in range (rows)]
	fields = cols * rows
	for color, colorAmount in enumerate(colorDistribution, start = 1):
		coloredFields = fields * colorAmount // colorSum
		for (x, y) in coords[:coloredFields]:
			board[y][x] = color
		coords = coords[coloredFields:]
	for color, (x, y) in enumerate(coords, start=1):
		board[y][x] = color

	oneLineBoard = '[[' + '],['.join([','.join([str(x) for x in a]) for a in board]) + ']]'

	return oneLineBoard

if len(sys.argv) >= 3:
	x = int(sys.argv[1])
	y = int(sys.argv[2])
else:
	x = 45
	y = 45

if len(sys.argv) >= 4:
	c = int(sys.argv[3])
else:
	c = 3

print(randomBoard(x, y, [1]*c))
