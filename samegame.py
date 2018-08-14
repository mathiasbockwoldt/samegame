import sys
import random
import copy
import time

class Board():
	'''
	A class to simulate a board of samegame as described in the competition guidelines at http://samegame.asta-wedel.de

	For initiation, it demands a board in the one-line representation (see guidelines) as a string.
	'''

	def __init__(self, grid):
		'''
		Initiating the board. See class description for details.
		'''

		# Read in board from one-line grid
		# Remove all spaces and the first and last two brackets
		grid = grid.replace(' ', '')[2:-2]
		# Save board as list of lists of integers
		self.board = []
		# Save the number of each color as a dictionary
		self.colors = {}
		for elem in grid.split('],['):
			row = []
			for a in elem.split(','):
				b = int(a)
				row.append(int(b))
				if b:
					if b not in self.colors:
						self.colors[b] = 0
					self.colors[b] += 1
			self.board.append(row)

		self.numOfColors = len(self.colors)

		# Save number of columns and rows
		self.columns = len(self.board)
		self.rows = len(self.board[0])

		# Save original number of columns and rows. Mainly used for printing a nice board :)
		self.origColumns = self.columns
		self.origRows = self.rows

		# Save number of colors (the length of a set of a flattened list minus one (because of 0))
		# self.numOfColors = len(set([b for a in self.board for b in a])) - 1

		# Save score for evaluation
		self.score = 0

		# Save moves
		self.moves = []


	def __str__(self):
		'''
		String representation of the board (simply do `print(self)`).
		'''

		lines = [str(self.rows) + 'x' + str(self.columns) + '@' + ','.join([str(self.colors[a]) for a in self.colors])]
		lines.append('Sc: ' + str(self.score) + ', tSc: ' + str(self.calcRemainingPoints()))

		for y in range(self.origRows - 1, -1, -1):
			line = str(y%10) + ' | '
			for x in range(self.origColumns):
				if not self.board[x][y]:
					line += '. '
				elif self.board[x][y] < 75:
					line += chr(self.board[x][y] + 48) + ' '
				else:
					line += str(self.board[x][y]) + ' '
			lines.append(line)

		lines.append('^y ' + '-'*(self.origColumns*2))
		lines.append('x-> ' + ' '.join([str(x%10) for x in range(self.origColumns)]))

		return '\n'.join(lines) + '\n'


	def floodFill(self, x, y):
		'''
		Returns all elements that belong to a field starting with a given coordinate. Uses a iterative floodfill algorithm using a not-so-standard queue approach using a set.
		This method does NOT change the board!

		:param x: The x-coordinate (column) of the element to start from
		:param y: The y-coordinate (row) of the element to start from
		:returns: A set of tuples with coordinates (x,y) that belong to the field
		'''

		color = self.board[x][y]
		if not color:
			return []
		toChange = set()
		toChange.add((x, y))
		toFill = set()
		toFill.add((x, y))
		while toFill:
			x, y = toFill.pop()

			toChange.add((x, y))

			if x > 0 and self.board[x-1][y] == color and (x-1, y) not in toChange:
				toFill.add((x-1, y))

			if x < self.columns - 1 and self.board[x+1][y] == color and (x+1, y) not in toChange:
				toFill.add((x+1, y))

			if y > 0 and self.board[x][y-1] == color and (x, y-1) not in toChange:
				toFill.add((x, y-1))

			if y < self.rows - 1 and self.board[x][y+1] == color and (x, y+1) not in toChange:
				toFill.add((x, y+1))

		return toChange


	def findAreas(self):
		'''
		Finds all clickable areas with more than one element in the board.
		'''

		inArea = set()
		areaEntries = []

		for x in range(self.columns):
			for y in range(self.rows):
				if self.board[x][y] and (x, y) not in inArea:
					area = self.floodFill(x, y)
					inArea.update(area)
					if len(area) > 1:
						areaEntries.append((x, y, len(area), area))

		return areaEntries


	def click(self, x, y, toChange=None):
		'''
		Performs a "click" on a board element. If the element is 0 or it has no neighbours with the same number, nothing happens. If it has at least one neighbour with the same number, the whole field is removed, gravity applies, and the player is rewarded with points for removing the field. The number of colors is updated.
		CHANGES THE BOARD IN PLACE!

		:param x: The x-coordinate (column) of the click
		:param y: The y-coordinate (row) of the click
		'''

		if self.board[x][y]:
			if toChange is None:
				toChange = self.floodFill(x, y)
			if len(toChange) > 1:
				self.colors[self.board[x][y]] -= len(toChange)
				for x, y in toChange:
					self.board[x][y] = 0
				self.applyGravity()
				self.score += self.calcScore(len(toChange))
				self.moves.append((x, y))


	def calcScore(self, n):
		'''
		Calculates the value (as described in the competition guidelines) of removed elements from the board given the number of removed elements.

		:param n: Number of removed elements
		:returns: The score, the player is rewarded for that turn
		'''

		if n > 1:
			return (n - 1) ** 2
		else:
			return 0


	def calcRemainingPoints(self):
		'''
		Calculates the value of all remaining elements according to the competition guidelines.

		:returns: The value of all remaining elements
		'''

		score = 0

		for c in self.colors:
			score += self.calcScore(self.colors[c])

		return score


	def applyGravity(self):
		'''
		Applies gravity to the board elements and removes empty columns.

		#### On https://github.com/Roxxik/SameGame/blob/master/old/core.py there is a nice, short algorithm. Test, if it's faster (for different board sizes etc.)!

		CHANGES THE BOARD IN PLACE!
		'''

		# starting in the second row from top
		for y in range(self.rows - 2, -1, -1):
			# starting from left
			for x in range(self.columns):
				if not self.board[x][y]:
					for newY in range(y, self.rows - 1):
						self.board[x][newY] = self.board[x][newY+1]
						self.board[x][newY+1] = 0
						if not self.board[x][newY]:
							break

		columnsSubtract = 0
		for x in range(self.columns - 1, -1, -1):
			if not self.board[x][0]:
				for newX in range(x, self.columns - 1):
					self.board[newX] = self.board[newX+1]
				columnsSubtract += 1

		for i in range(columnsSubtract):
			self.board[self.columns - i - 1] = [0] * self.origRows
		self.columns -= columnsSubtract

		self.rows = self.getHeight()


	def getHeight(self):
		'''
		Determines the active height of the board (that is, the maximum height of any non-zero number)

		:returns: The current active height
		'''

		toSubtract = 0

		for y in range(self.rows - 1, -1, -1):
			for x in range(self.columns):
				if self.board[x][y]:
					return self.rows - toSubtract
			toSubtract += 1

		return 0


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# #                                                                 # #
# #                        AIs start here                           # #
# #                                                                 # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


def playShortsightedBestField(board):
	'''
	AI. Simply clicks on the largest available field until no more clickable fields are available. Prints the field after each move to stdout and infos (if available) to stderr. Finally, returns a string with moves.

	:returns: A string with all moves.
	'''

	availableFields = board.findAreas()
	print(availableFields)
	while availableFields:
		# sort available fields by score, then taking the one with the uppermost entry point to not destroy structures above it; chose the best field
		bestField = sorted(availableFields, key=lambda x: (x[2], x[1]))[-1]
		print('next move: ' + str(bestField[0]) + ',' + str(bestField[1]))
		print(board)
		# click the best field
		board.click(bestField[0], bestField[1])
		# update available fields
		availableFields = board.findAreas()

	print('next move: No more moves')
	print(board)
	board.score -= board.calcRemainingPoints()
	print('final score:', board.score)

	return '[(' + '),('.join([str(x) + ',' + str(y) for x, y in board.moves]) + ')]'


def playShortsightedWorstField(board):
	'''
	AI. Simply clicks on the smallest available field until no more clickable field are available. Prints the field after each move to stdout and infos (if available) to stderr. Finally, returns a string with moves.

	:returns: A string with all moves.
	'''

	availableFields = board.findAreas()
	while availableFields:
		# sort available fields by score
		worstField = sorted(availableFields, key=lambda x: x[2])[0]
		print('next move: ' + str(worstField[0]) + ',' + str(worstField[1]))
		print(board)
		# click the best field
		board.click(worstField[0], worstField[1])
		# update available fields
		availableFields = board.findAreas()

	print('next move: No more moves')
	print(board)
	board.score -= board.calcRemainingPoints()
	print('final score:', board.score)

	return '[(' + '),('.join([str(x) + ',' + str(y) for x, y in board.moves]) + ')]'


def playGraphBasedBasic(board):
	'''
	AI. Attempt of an AI that makes a graph of all possible moves and traversing it via BFS-like (breadth-first-search).
	'''

	bestBoard = board
	newList = []
	oldList = [board]

	while oldList:
		for b in oldList:
			clickables = b.findAreas()
			if not clickables:
				if b.score > bestBoard.score:
					bestBoard = b
				continue
			for c in clickables:
				bNew = copy.deepcopy(b)
				bNew.click(c[0], c[1])
				newList.append(bNew)
		oldList = newList
		newList = []
		print(bestBoard.score, len(oldList))

	return bestBoard.moves

#@profile
def playGraphBasedNoDoubleBoards(board):
	'''
	AI. Attempt of an AI that makes a graph of all possible moves and traversing it via BFS-like (breadth-first-search). It consideres boards that occur twice and only uses the best of the two:
	       .23    .2.
	123 -> .23 -> .2. <,
	123                +-- These two boards are equal but usually spaw new branches
	    -> 12. -> .2. <'
	       12.    .2.
	'''

	##### Deepcopy needs about 85% of the total run time.

	bestBoard = board
	newList = []
	oldList = [board]
	knownBoards = set()
	knownBoardsScore = {}

	while oldList:
		for b in oldList:
			clickables = b.findAreas()
			if not clickables:
				b.score -= b.calcRemainingPoints()
				if b.score > bestBoard.score:
					bestBoard = b
				continue
			for c in clickables:
				bNew = copy.deepcopy(b)
				bNew.click(c[0], c[1], c[3])
				boardHash = hash(repr(bNew.board))
				if boardHash in knownBoards:
					if knownBoardsScore[boardHash] < bNew.score:
						knownBoardsScore[boardHash] = bNew.score
						newList.append(bNew)
				else:
					knownBoards.add(boardHash)
					knownBoardsScore[boardHash] = bNew.score
					newList.append(bNew)
		oldList = newList
		newList = []
		print(bestBoard.score, len(oldList))

	return bestBoard.moves


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# #                                                                 # #
# #                Helper functions start here                      # #
# #                                                                 # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


def runSequence(board, sequence):
	'''
	Applies a given sequence on a given board.

	:param board: Board object on which to apply the sequence
	:param sequence: List of tuples with coordinates of fields to click
	'''

	print('Next move: ' + str(sequence[0]))
	print(board)

	for i, c in enumerate(sequence):
		board.click(c[0], c[1])
		if i < len(sequence)-1:
			print('Next move: ' + str(sequence[i+1]))
		else:
			print('Next move: No more moves')
		print(board)

	print('Final score: ' + str(board.score - board.calcRemainingPoints()))


def usage():
	'''
	Prints program usage.
	'''

	print('Usage:')
	print('Input via stdin: python3 samegame.py')
	print('Input via argument: python3 samegame.py [[0, 1],[0, 1]]')
	print('Input from file with one line in file: python3 samegame.py filename.txt')
	print('Input from file as grid (tsv): python3 samegame.py grid filename.txt')
	print('Random board with size 8 x 5 and color distribution 1,2,1,1: python3 samegame.py 8 5 1,2,1,1')
	print('Random board as above with seed 42: python3 samegame.py 8 5 1,2,1,1 42')


def gridToOneLine(s):
	'''
	Converts a board in tab-separated format to the one-line format described in the competition guidelines.

	:param s: The board in tab-separated format
	:returns: The board in one-line format
	'''

	grid = []
	for line in s.split('\n'):
		grid.append(', '.join(line.split()))

	return '[[' + '], ['.join(grid) + ']]'


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


testgrid = '[[3,2,3,3,1,1,2,3,1,1,2,3],[3,2,2,1,1,3,3,3,1,2,2,1],[3,3,2,1,1,1,2,3,1,1,2,3],[3,2,2,1,1,2,3,3,2,3,2,2],[1,2,3,1,1,3,2,3,3,2,3,1],[2,3,1,1,2,1,1,3,1,2,3,1],[1,3,2,2,3,2,1,2,2,3,1,1]]'


if __name__ == "__main__":

	board = False

	# If no argument is given, ask for the field via STDIN.
	# If one argument is given and it is `-h`, print usage, if the argument is `test`, use the testboard. In any other case, assume that the argument is the board.
	# If two arguments are given assume that the second argument is a filename with the grid. The style of the grid in the file depends on the first argument (`oneline`: as usual; `grid`: in tsv format). If the keyword is missing, or the file does not exist, print usage.
	# If three or four arguments are given, generate a random board with the first arg as width, second as height and third as color distribution. The optional fourth argument serves as seed for the pseudo-random number generator

	if len(sys.argv) == 1:
		board = Board(input('Enter the field in one line: '))
	elif len(sys.argv) == 2:
		if sys.argv[1] == 'test':
			board = Board(testgrid)
		elif sys.argv[1] == '-h':
			usage()
		else:
			board = Board(sys.argv[1])
	elif len(sys.argv) == 3:
		try:
			with open(sys.argv[2], 'r') as f:
				if sys.argv[1] == 'oneline':
					board = Board(f.read().rstrip())
				elif sys.argv[1] == 'grid':
					board = Board(gridToOneLine(f.read().rstrip()))
				else:
					usage()
		except OSError:
			print('Could not find file {}'.format(sys.argv[2]))
			usage()
	elif len(sys.argv) == 4:
		board = Board(randomBoard(int(sys.argv[1]), int(sys.argv[2]), [int(x) for x in sys.argv[3].split(',')]))
	elif len(sys.argv) == 5:
		board = Board(randomBoard(int(sys.argv[1]), int(sys.argv[2]), [int(x) for x in sys.argv[3].split(',')], int(sys.argv[4])))
	else:
		usage()

	#if board:
	#	runSequence(board, [(1, 1), (2, 2), (2, 2), (4, 0), (5, 3), (5, 3), (4, 0), (4, 0), (4, 0)])

	#quit()

	if board:
		now = time.clock()
		print(playShortsightedBestField(board), file=sys.stderr)
		print(time.clock()-now)
