import os
import numpy as np
import itertools
import time
import copy
from tqdm import tqdm


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
        block = {}
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
            elif line[0].isupper() is True:
                if line[0] == 'L':
                    line = line.split(' ')
                    for i in range(len(line)):
                        try:
                            line[i] = int(line[i])
                        except:
                            continue
                    laser.append([(line[1], line[2]), (line[1] + line[3], line[2] + line[4])])
                elif line[0] == 'P':
                    line = line.split(' ')
                    for i in range(len(line)):
                        try:
                            line[i] = int(line[i])
                        except:
                            continue
                    points.append((line[1], line[2]))
                else:
                    if line[2].isdigit() is True:
                        block[line[0]] = int(line[2])
                    else:
                        a = []
                        for i in line:
                            if i.isalpha() is True:
                                a.append(i)
                            else:
                                continue
                        grid.append(a)
            else:
                a = []
                for i in line:
                    if i.isalpha() is True:
                        a.append(i)
                    else:
                        continue
                grid.append(a)
        print(laser)
        # print(block)
        print(points)
        # print(grid)
        # grid_matrix = np.zeros((2*len(grid)+1, 2*len(grid[0])+1))
        # for i in range(len(grid)):
        #     for ii in range(len(grid[0])):
        #         if grid[i][ii] == 'x':
        #             x_cord = 2*i + 1
        #             y_cord = 2*ii + 1
        #             grid_matrix[x_cord + 1][y_cord] = 1
        #             grid_matrix[x_cord][y_cord] = 1
        #             grid_matrix[x_cord - 1][y_cord] = 1
        #             grid_matrix[x_cord + 1][y_cord - 1] = 1
        #             grid_matrix[x_cord][y_cord - 1] = 1
        #             grid_matrix[x_cord - 1][y_cord - 1] = 1
        #             grid_matrix[x_cord + 1][y_cord + 1] = 1
        #             grid_matrix[x_cord][y_cord + 1] = 1
        #             grid_matrix[x_cord - 1][y_cord + 1] = 1
        #         else:
        #             continue
        # print(grid_matrix)
        for i in range(len(grid)):
            for ii in range(len(grid[0])):
                if grid[i][ii] != 'o':
                    continue
                else:
                    possible_position.append((ii, i))

        # print(possible_position)
        fixed = fix_block(grid)
        # print(fixed)
        fixed_class = []
        if fixed == []:
            pass
        else:
            for i in fixed:
                fixed_class.append((Block(i[0]), i[1]))
        # print(fixed_class)
        block_total = 0
        for i in block:
            block_total += block[i]
        for i in itertools.combinations(possible_position, block_total):
            if len(block) == 2:
                keys = list(block.keys())
                num1 = block.get(keys[0])
                num2 = block.get(keys[1])
                for ii in itertools.combinations(i, num1):
                    block_class = []
                    possible_block_position = list(ii)
                    cross = list(set(i) ^ set(ii))
                    # print(i, possible_block_position, cross)
                    for j in range(num1):
                        block_class.append((Block(possible_block_position[-1]), keys[0]))
                        possible_block_position.pop()
                    for k in range(num2):
                        block_class.append((Block(cross[-1]), keys[1]))
                        cross.pop()
                    block_class.extend(fixed_class)
                    find_solution(block_class, laser, points)
                    # print(block_class)
                    a = find_solution(block_class, laser, points)
                    if a is True:
                        print(a, i)
                        break
                    else:
                        continue
            elif len(block) == 3:
                num1 = block.get('A')
                num2 = block.get('B')
                num3 = block.get('C')
                for ii in itertools.combinations(i, num1):
                    block_class = []
                    possible_block_position = list(ii)
                    cross = list(set(i) ^ set(ii))
                    for j in range(num1):
                        block_class.append((Block(possible_block_position[-1]), 'A'))
                        possible_block_position.pop()
                    for iii in itertools.combinations(cross, num2):
                        cross2 = list(set(cross) ^ set(iii))
                        possible_block_position2 = list(iii)
                        for k in range(num2):
                            block_class.append((Block(possible_block_position2[-1]), 'B'))
                            possible_block_position2.pop()
                        for kk in range(num3):
                            block_class.append((Block(cross2[-1]), 'C'))
                            cross2.pop()

            else:
                block_class = []
                possible_block_position = list(i)
                for ii in range(block_total):
                    block_class.append((Block(possible_block_position[-1]), list(block.keys())[0]))
                    possible_block_position.pop()
                block_class.extend(fixed_class)
                # print(block_class)
                a = find_solution(block_class, laser, points)
                # print(a, i)
                if a is True:
                    if (2, 1) in i:
                        continue
                    else:
                        print(a, i)
                else:
                    continue
                # print(find_solution(block_class, laser, points), i)
                # print(block_class)

def find_solution(block_class, laser, goal):
    target = copy.deepcopy(goal)
    laser2 = copy.deepcopy(laser)
    while True:
        length = len(laser2)
        possible_candidate = set()
        length2 = len(possible_candidate)
        update_laser = copy.deepcopy(laser2)
        possible_reflect = set()
        for block in block_class:
            if block[1] == 'B':
                for cord in laser2:
                    _, candidate, out_point = block[0].opaque(cord[0], cord[1])
                    if candidate != 'none':
                        possible_candidate.add((candidate, 'B'))
                        if candidate == cord[0] and cord in laser2:
                            update_laser.remove(cord)
                        else:
                            pass
                    else:
                        pass
                for cord in update_laser:
                    l = Laser(cord[0], cord[1])
                    _, candidate, out_point = block[0].opaque(cord[0], cord[1])
                    for i in target:
                        if candidate != 'none':
                            if l.laser_intersect_or_not(i) is True and l.between_two_point_or_not(candidate, i) is True:
                                target.remove(i)
                            else:
                               pass
                        else:
                            pass
            elif block[1] == 'A':
                pass
                count4 = 0
                for cord in laser2:
                    l = Laser(cord[0], cord[1])
                    _, candidate, out_point = block[0].reflect(cord[0], cord[1])
                    if candidate != 'none':
                        if out_point != 'none':
                            if [candidate, out_point] in update_laser:
                                pass
                            else:
                                update_laser.append([candidate, out_point])
                        else:
                            pass
                        possible_candidate.add((candidate, 'A'))
                        count4 += 1
                        possible_reflect.add((candidate, count4))
                        for i in target:
                            if l.laser_intersect_or_not(i) is True and l.between_two_point_or_not(candidate,i) is True:
                                if i in target:
                                    target.remove(i)
                                else:
                                    pass
                            else:
                                pass
                    else:
                        pass
            else:
                for cord in laser2:
                    _, candidate, out_point = block[0].refract(cord[0], cord[1])
                    if candidate != 'none':
                        possible_candidate.add((candidate, 'C'))
                        for i in target:
                            if l.laser_intersect_or_not(i) is True and l.between_two_point_or_not(candidate, i) is True:
                                if i in target:
                                    target.remove(i)
                                else:
                                    pass
                            else:
                                pass
                    else:
                        pass
                    if candidate != 'none' and out_point[0] != 'none':
                        if [candidate, out_point[0]] in update_laser:
                            pass
                        else:
                            update_laser.append([candidate, out_point[0]])
                    else:
                        pass
                    if candidate != 'none' and out_point[1] != 'none':
                        if [candidate, out_point[1]] in update_laser:
                            pass
                        else:
                            update_laser.append([candidate, out_point[1]])
                    else:
                        pass
        possible_candidate2 = list(possible_candidate)
        print(possible_candidate2, possible_reflect)
        if possible_candidate2[-1][1] == 'A':
            pass
        else:
            pass
        # for i in possible_candidate:
        #     if i[1]

        # print(update_laser)
        # print(laser2)
        for cord2 in update_laser:
            l = Laser(cord2[0], cord2[1])
            for i in target:
                if len(possible_candidate) == 0:
                    if l.laser_intersect_or_not(i) is True:
                        if i in target:
                            target.remove(i)
                        else:
                            pass
                    else:
                        pass
                else:
                    count = 0
                    for ii in possible_candidate:
                        if ii[1] == 'B' or ii[1] == 'A':
                            if l.laser_intersect_or_not(ii[0]) is True:
                                ll = Laser(cord2[0], ii[0])
                                if ll.laser_intersect_or_not(i) is True and ll.between_two_point_or_not(ii[0], i) is True:
                                    if i in target:
                                        target.remove(i)
                                    else:
                                        pass
                                else:
                                    pass
                            else:
                                count += 1
                        else:
                            if l.laser_intersect_or_not(i) is True and i in target:
                                target.remove(i)
                            else:
                               pass
                    if count == len(possible_candidate):
                        if l.laser_intersect_or_not(i) is True and i in target:
                            target.remove(i)
                        else:
                            pass
        if target == []:
            # print(possible_candidate)
            return True
        else:
            laser2 = update_laser
            if length == len(laser2):
                return False
            else:
                continue








def fix_block(grid):
    position_category = []
    for i in range(len(grid)):
        for ii in range(len(grid[0])):
            if grid[i][ii].isupper() is True:
                position_category.append([(ii, i), grid[i][ii]])
            else:
                continue
    return position_category



class Laser(object):
    def __init__(self, position1, position2):
        self.position1 = position1
        self.position2 = position2
    def line(self):
        k = (self.position1[1] - self.position2[1]) / (self.position1[0] - self.position2[0])
        b = self.position1[1] - k * self.position1[0]
        return k, b
    def laser_intersect_or_not(self, query):
        self.query = query
        k, b = Laser.line(self)
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
    def between_two_point_or_not(self, candidate, query):
        self.query = query
        self.candidate = candidate
        x_cord = [self.candidate[0], self.position1[0]]
        y_cord = [self.candidate[1], self.position1[1]]
        if self.query[0] >= min(x_cord) and self.query[1] >= min(y_cord) and self.query[0] <= max(x_cord) and self.query[1] <= max(y_cord):
            return True
        else:
            return False






class Block(object):
    def __init__(self, block_position):
        self.block_position = block_position
    def intersect_point(self):
        x_cord = 2 * self.block_position[0] + 1
        y_cord = 2 * self.block_position[1] + 1
        intersect_surface = {(x_cord, y_cord - 1): 'up', (x_cord, y_cord + 1): 'down',
                          (x_cord - 1, y_cord): 'left', (x_cord + 1, y_cord): 'right'}
        intersect_point = [(x_cord, y_cord - 1), (x_cord, y_cord + 1), (x_cord - 1, y_cord), (x_cord + 1, y_cord)]
        return intersect_point, intersect_surface
    def reflect(self, laser_origin_point, incoming_laser_point):
        self.k, self.b = Laser(laser_origin_point, incoming_laser_point).line()
        self.incoming_laser_point = incoming_laser_point
        self.origin_point = laser_origin_point
        intersect_point, intersect_surface = Block.intersect_point(self)
        min_distance = float('inf')
        candidate = 'none'
        out_point = 'none'
        laser_in_block = copy.deepcopy(intersect_point)
        if self.origin_point in laser_in_block:
            laser_in_block.remove(self.origin_point)
            for i in laser_in_block:
                if Laser(self.origin_point, self.incoming_laser_point).laser_intersect_or_not(i) is True:
                    self.k = -1 / self.k
                    self.b = self.origin_point[1] - self.k * self.origin_point[0]
                    candidate = self.origin_point
                    surface = intersect_surface.get(i)
                    if surface == 'left' or surface == 'right':
                        # print(self.k, self.b)
                        out_point = (self.incoming_laser_point[0], self.k * self.incoming_laser_point[0] + self.b)
                    else:
                        out_point = ((self.incoming_laser_point[1] - self.b) / self.k, self.incoming_laser_point[1])
                else:
                    pass
        else:
            for i in intersect_point:
                if Laser(self.origin_point, self.incoming_laser_point).laser_intersect_or_not(i) is True:
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

        return [(self.k, self.b)], candidate, out_point
    def opaque(self, laser_origin_point, incoming_laser_point):
        self.k, self.b = Laser(laser_origin_point, incoming_laser_point).line()
        self.incoming_laser_point = incoming_laser_point
        self.origin_point = laser_origin_point
        intersect_point, intersect_surface = Block.intersect_point(self)
        min_distance = float('inf')
        candidate = 'none'
        laser_in_block = copy.deepcopy(intersect_point)
        if self.origin_point in laser_in_block:
            laser_in_block.remove(self.origin_point)
            for i in laser_in_block:
                if Laser(self.origin_point, self.incoming_laser_point).laser_intersect_or_not(i) is True:
                    candidate = self.origin_point
                else:
                    pass
        else:
            for i in intersect_point:
                if Laser(self.origin_point, self.incoming_laser_point).laser_intersect_or_not(i) is True:
                    update = np.linalg.norm(np.array(i) - np.array(self.origin_point))
                    if update < min_distance:
                        min_distance = update
                        candidate = i
                    else:
                        pass
                else:
                    pass
        self.k = 'none'
        self.b = 'none'
        out_point = 'none'
        return [(self.k, self.b)], candidate, out_point
    def refract(self, laser_origin_point, incoming_laser_point):
        self.k, self.b = Laser(laser_origin_point, incoming_laser_point).line()
        self.incoming_laser_point = incoming_laser_point
        self.origin_point = laser_origin_point
        k_origin = self.k
        b_origin = self.b
        intersect_point, intersect_surface = Block.intersect_point(self)
        min_distance = float('inf')
        candidate = 'none'
        out_point2 = 'none'
        out_point = 'none'
        laser_in_block = copy.deepcopy(intersect_point)
        if self.origin_point in laser_in_block:
            laser_in_block.remove(self.origin_point)
            for i in laser_in_block:
                if Laser(self.origin_point, self.incoming_laser_point).laser_intersect_or_not(i) is True:
                    self.k = -1 / self.k
                    self.b = self.origin_point[1] - self.k * self.origin_point[0]
                    candidate = self.origin_point
                    surface = intersect_surface.get(i)
                    if surface == 'left' or surface == 'right':
                        # print(self.k, self.b)
                        out_point = (self.incoming_laser_point[0], self.k * self.incoming_laser_point[0] + self.b)
                        out_point2 = self.incoming_laser_point
                    else:
                        out_point = ((self.incoming_laser_point[1] - self.b) / self.k, self.incoming_laser_point[1])
                        out_point2 = self.incoming_laser_point

                else:
                    pass
        else:
            for i in intersect_point:
                if Laser(self.origin_point, self.incoming_laser_point).laser_intersect_or_not(i) is True:
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



if __name__ == "__main__":
    start = time.time()
    # Input_file("bff")
    b = Block((2, 3))
    b2 = Block((2, 2))
    b3 = Block((1, 0))
    b4 = Block((0, 1))
    b5 = Block((3, 3))
    block_class = [(b, 'A'), (b2, 'A'), (b3, 'A'), (b4, 'A'), (b5, 'A')]
    print(find_solution(block_class, [[(7, 2), (6, 3)]], [(3, 4), (7, 4), (5, 8)]))
    # print(b.opaque((3, 0), (2, 1)))
    # print(b.opaque((1, 6), (2, 5)))
    # print(b.opaque((3, 6), (2, 5)))
    # print(b.opaque((4, 3), (5, 2)))
    # b = {1:'h', 2:'a', 3:'g'}
    # print(1 in b)
    # b[4] = []
    # print(b)
    end = time.time()
    print(end - start)
    # l = Laser((2, 3), (4, 5))
    # print(l.laser_intersect_or_not((6, 7)))
    # x = set()
    # x.add((1,2))
    # x.add((2,3))
    # x.add((3,4))
    # print(x)
    # for i in x:
    #     print(i)
    # b = Block((0, 0))
    # print(b.refract((3, 4), (2, 3)))

