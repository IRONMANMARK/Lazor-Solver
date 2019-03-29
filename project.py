import os
import numpy as np

def Input_file(path):
    name_list = []
    file_list = []
    for fpathe, dirs, i in os.walk(path):
        for ff in i:
            a = ff.split('.')
            name_list.append(a[0])
            file_list.append(os.path.join(fpathe, ff))
    # print(file_list)
    for i in file_list:
        f = open(i)
        grid = []
        laser =[]
        points = []
        block = []
        for line in f.readlines():
            line = line.strip('\n')
            if line == 'GRID START':
                continue
            elif line == '':
                continue
            elif line == 'GRID STOP':
                continue
            elif line[0] == '#':
                continue
            elif line[0].isupper() == True:
                if line[0] == 'L':
                    laser.append(line)
                elif line[0] == 'P':
                    points.append(line)
                else:
                    block.append(line)
            else:
                a = []
                for i in line:
                    if i.isalpha() == True:
                        a.append(i)
                    else:
                        continue
                grid.append(a)
        # print(laser)
        # print(block)
        # print(points)

        print(grid)
        grid_matrix = np.zeros((2*len(grid)+1, 2*len(grid[0])+1))
        for i in range(len(grid)):
            for ii in range(len(grid[0])):
                if grid[i][ii] == 'x':
                    x_cord = 2*i + 1
                    y_cord = 2*ii + 1
                    grid_matrix[x_cord + 1][y_cord] = 1
                    grid_matrix[x_cord][y_cord] = 1
                    grid_matrix[x_cord - 1][y_cord] = 1
                    grid_matrix[x_cord + 1][y_cord - 1] = 1
                    grid_matrix[x_cord][y_cord - 1] = 1
                    grid_matrix[x_cord - 1][y_cord - 1] = 1
                    grid_matrix[x_cord + 1][y_cord + 1] = 1
                    grid_matrix[x_cord][y_cord + 1] = 1
                    grid_matrix[x_cord - 1][y_cord + 1] = 1
                else:
                    continue
        print(grid_matrix)






if __name__ == "__main__":
    Input_file("bff")