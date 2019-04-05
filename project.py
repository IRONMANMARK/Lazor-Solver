import os
import numpy as np
import itertools

def Input_file(path):
    name_list = []
    file_list = []
    for fpathe, dirs, i in os.walk(path):
        for ff in i:
            a = ff.split('.')
            if a[1] == 'bff':
                name_list.append(a[0])
                file_list.append(os.path.join(fpathe, ff))
            else:
                continue
    for i in file_list:
        f = open(i)
        grid = []
        laser =[]
        points = []
        block = []
        possible_position = []
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
                    if line[2].isdigit() == True:
                        block.append(line)
                    else:
                        a = []
                        for i in line:
                            if i.isalpha() == True:
                                a.append(i)
                            else:
                                continue
                        grid.append(a)
            else:
                a = []
                for i in line:
                    if i.isalpha() == True:
                        a.append(i)
                    else:
                        continue
                grid.append(a)
        print(laser)
        print(block)
        print(points)

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
        # print(grid_matrix)
        for i in range(len(grid)):
            for ii in range(len(grid[0])):
                if grid[i][ii] != 'o':
                    continue
                else:
                    possible_position.append((ii, i))

        print(possible_position)


class laser(object):
    def __init__(self, position1, position2, query):
        self.position1 = position1
        self.position2 = position2
        self.query = query
    def line(self):
        k = (self.position1[1] - self.position2[1]) / (self.position1[0] - self.position2[0])
        b = self.position1[1] - k * self.position1[0]
        return k, b
    def laser_intersect_or_not(self):
        k, b = laser.line(self)
        laser_vector = (self.position2[0] - self.position1[0], self.position2[1] - self.position1[1])
        query_vector = (self.query[0] - self.position1[0], self.query[1] - self.position1[1])
        vector_align = laser_vector[0] * query_vector[1] - query_vector[0] * laser_vector[1]
        if self.query[0] * k + b == self.query[1]:
            if vector_align == 0 and query_vector[0] / laser_vector[0] > 0:
                return True
            else:
                return False
        else:
            return False

class block(object):
    def __init__(self, block_position, laser_origin_point, incoming_laser_point, k, b):
        self.block_position = block_position
        self.k = k
        self.b = b
        self.incoming_laser_point = incoming_laser_point
        self.origin_point = laser_origin_point
    def intersect_point(self):
        x_cord = 2 * self.block_position[0] + 1
        y_cord = 2 * self.block_position[1] + 1
        intersect_surface = {(x_cord, y_cord - 1): 'up', (x_cord, y_cord + 1): 'down',
                          (x_cord - 1, y_cord): 'left', (x_cord + 1, y_cord): 'right'}
        intersect_point = [(x_cord, y_cord - 1), (x_cord, y_cord + 1), (x_cord - 1, y_cord), (x_cord + 1, y_cord)]
        return intersect_point, intersect_surface
    def reflect(self):
        intersect_point, intersect_surface = block.intersect_point(self)
        min_distance = float('inf')
        candidate = 'none'
        if self.origin_point in intersect_point and self.incoming_laser_point in intersect_point:
            self.k = -1 / self.k
            self.b = self.origin_point[1] - self.k * self.origin_point[0]
            out_point = (self.incoming_laser_point[0], self.k * self.incoming_laser_point[0] + self.b)
            candidate = self.origin_point
        else:
            for i in intersect_point:
                if laser(self.origin_point, self.incoming_laser_point, i).laser_intersect_or_not() == True:
                    update = np.linalg.norm(np.array(i) - np.array(self.origin_point))
                    if update < min_distance:
                        min_distance = update
                        candidate = i
                    else:
                        continue
                else:
                    continue
            if candidate != 'none':
                self.k = -1 / self.k
                self.b = candidate[1] - self.k * candidate[0]
                surface = intersect_surface.get(candidate)
                if surface == 'left' or surface == 'right':
                    # print(self.k, self.b)
                    out_point = (self.origin_point[0], self.k * self.origin_point[0] + self.b)
                else:
                    out_point = ((self.origin_point[1] - self.b) / self.k, self.origin_point[1])
            else:
                out_point = 'none'

        return self.k, self.b, candidate, out_point
    def opaque(self):
        intersect_point, intersect_surface = block.intersect_point(self)
        min_distance = float('inf')
        candidate = 'none'
        if self.origin_point in intersect_point and self.incoming_laser_point in intersect_point:
            candidate = self.origin_point
        else:
            for i in intersect_point:
                if laser(self.origin_point, self.incoming_laser_point, i).laser_intersect_or_not() == True:
                    update = np.linalg.norm(np.array(i) - np.array(self.origin_point))
                    if update < min_distance:
                        min_distance = update
                        candidate = i
                    else:
                        continue
                else:
                    continue
        self.k = 'none'
        self.b = 'none'
        out_point = 'none'
        return self.k, self.b, candidate, out_point
    def refract(self):
        k_origin = self.k
        b_origin = self.b
        intersect_point, intersect_surface = block.intersect_point(self)
        min_distance = float('inf')
        candidate = 'none'
        if self.origin_point in intersect_point and self.incoming_laser_point in intersect_point:
            self.k = -1 / self.k
            self.b = self.origin_point[1] - self.k * self.origin_point[0]
            out_point = (self.incoming_laser_point[0], self.k * self.incoming_laser_point[0] + self.b)
            candidate = self.origin_point
            out_point2 = self.incoming_laser_point
        else:
            for i in intersect_point:
                if laser(self.origin_point, self.incoming_laser_point, i).laser_intersect_or_not() == True:
                    update = np.linalg.norm(np.array(i) - np.array(self.origin_point))
                    if update < min_distance:
                        min_distance = update
                        candidate = i
                    else:
                        continue
                else:
                    continue
            if candidate != 'none':
                self.k = -1 / self.k
                self.b = candidate[1] - self.k * candidate[0]
                surface = intersect_surface.get(candidate)
                if surface == 'left' or surface == 'right':
                    # print(self.k, self.b)
                    out_point = (self.origin_point[0], self.k * self.origin_point[0] + self.b)
                else:
                    out_point = ((self.origin_point[1] - self.b) / self.k, self.origin_point[1])
                out_point2 = (2 * candidate[0] - self.origin_point[0], 2 * candidate[1] - self.origin_point[1])
            else:
                out_point = 'none'
                out_point2 = 'none'


        return [(self.k, self.b), (k_origin, b_origin)], candidate, [out_point, out_point2]


# def find_solution():







if __name__ == "__main__":
    Input_file("bff")
    a = laser((3, 4), (2, 3), 2).line()
    b = block((1, 2), (2, 3), (3, 4), 1, 1)
    print(b.refract())

