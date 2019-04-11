# import project

# position, grid = project.Input_file('bff')


cllll = [((3, 5), 'A'), ((1, 5), 'A'), ((4, 4), 'A'), ((0, 4), 'A'), ((2, 3), 'A'), ((4, 2), 'A'), ((0, 2), 'A'), ((1, 1), 'A')]
grid = [['o', 'B', 'x', 'o', 'o'], ['o', 'o', 'o', 'o', 'o'], ['o', 'x', 'o', 'o', 'o'], ['o', 'x', 'o', 'o', 'x'], ['o', 'o', 'x', 'x', 'o'], ['B', 'o', 'x', 'o', 'o']]


def out_put(cllll, grid):
	blockpositions = []
	for i in cllll:
		x,y = i[0]
		blocksymbol = i[1]
		grid[y][x] = str(blocksymbol)
	f = open("solution_grid.txt","w+")
	f.write(str(grid))


print out_put(cllll,grid)
