import sys

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


if __name__ == "__main__":
	grid = '[[4,2,4,2,1,3],[4,3,2,1,3,1],[2,3,4,1,1,1],[1,1,2,3,3,1],[1,1,2,1,2,3],[2,3,4,1,1,2]]'
	seq = [(1, 0),(0, 0),(0, 0),(3, 0),(0, 0),(0, 0),(0, 0),(0, 0)]
	runSequence(Board(grid), seq)
