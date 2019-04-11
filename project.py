import os
import numpy as np
import itertools
import time
import copy
import operator
import numba
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
                    laser.append([(line[1], line[2]), (line[1] + line[3], line[2] + line[4]), True])
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
            b = 0
            if len(block) == 2:
                keys = list(block.keys())
                num1 = block.get(keys[0])
                num2 = block.get(keys[1])
                for ii in itertools.combinations(i, num1):
                    block_class = []
                    cllll = []
                    possible_block_position = list(ii)
                    cross = list(set(i) ^ set(ii))
                    # print(i, possible_block_position, cross)
                    for j in range(num1):
                        block_class.append((Block(possible_block_position[-1]), keys[0]))
                        cllll.append((possible_block_position[-1], keys[0]))
                        possible_block_position.pop()
                    for k in range(num2):
                        block_class.append((Block(cross[-1]), keys[1]))
                        cllll.append((cross[-1], keys[1]))
                        cross.pop()

                    block_class.extend(fixed_class)
                    # print(ii, i, block_class)
                    a = find_solution(block_class, laser, points)
                    # print(a, i)
                    if a is True:
                        b = 2
                        print(a, ii, i)
                        break
                    else:
                        continue
                if b == 2:
                    break
                else:
                    pass

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
                cllll = []
                possible_block_position = list(i)
                for ii in range(block_total):
                    block_class.append((Block(possible_block_position[-1]), list(block.keys())[0]))
                    cllll.append((possible_block_position[-1], list(block.keys())[0]))
                    possible_block_position.pop()
                block_class.extend(fixed_class)
                # print(block_class)
                a = find_solution(block_class, laser, points)
                # print(a, i)
                if a is True:
                    print(a)
                    break
                else:
                    continue
                # print(find_solution(block_class, laser, points), i)
                # print(block_class)
        print(cllll)
        print(grid)


def find_solution(block_class, laser, goal):
    target = copy.deepcopy(goal)
    laser2 = copy.deepcopy(laser)
    count = 0
    count2 = 0
    stop = []
    contain = []
    result = []
    update_laser3 = []
    while True:
        if count > 1:
            result.extend(update_laser3)
            break
        else:
            pass
        possible_candidate = set()
        update_laser = copy.deepcopy(laser2)
        mid = {}
        update_laser2 = []
        update_laser4 = []
        refract_candidate = []
        for cord in laser2:
            distance = float('inf')
            candidate2 = 'none'
            out_point2 = 'none'
            candidate3 = 'none'
            out_point3 = 'none'
            for block in block_class:
                if block[1] == 'A':
                    _, candidate, out_point = block[0].reflect(cord[0], cord[1])
                    if candidate != 'none':
                        possible_candidate.add((candidate, out_point, 'A'))
                        update_dis = np.linalg.norm(np.array(candidate) - np.array(cord[0]))
                        if update_dis < distance:
                            distance = update_dis
                            candidate3 = candidate
                            out_point3 = out_point
                            if cord[0] != candidate:
                                update_laser[laser2.index(cord)] = [cord[0], candidate, False]
                                # mid[cord[0]] = [candidate, out_point, True]
                            else:
                                update_laser[laser2.index(cord)] = [cord[0], out_point, True]
                                if cord in contain:
                                    pass
                                else:
                                    contain.append(cord)
                                # mid[cord[0]] = [candidate, out_point, True]
                        else:
                            pass
                    else:
                        pass
                elif block[1] == 'B':
                    _, candidate, out_point = block[0].opaque(cord[0], cord[1])
                    if candidate != 'none':
                        possible_candidate.add((candidate, out_point, 'B'))
                        update_dis = np.linalg.norm(np.array(candidate) - np.array(cord[0]))
                        if update_dis < distance:
                            distance = update_dis
                            candidate3 = candidate
                            out_point3 = out_point
                            if cord[0] != candidate:
                                update_laser[laser2.index(cord)] = [cord[0], candidate, False]
                            else:
                                update_laser[laser2.index(cord)] = [cord[0], 'none', False]
                        else:
                            pass
                    else:
                        pass
                else:
                    _, candidate, out_point = block[0].refract(cord[0], cord[1])
                    if candidate != 'none':
                        if cord[0] != candidate:
                            candidate2 = candidate
                            out_point2 = out_point
                        else:
                            if [candidate, out_point[0], True] in contain:
                                pass
                            else:
                                if [cord[0], out_point[0], True] in update_laser2:
                                    if [cord[0], out_point[1], True] in update_laser2:
                                        pass
                                    else:
                                        update_laser2.append([cord[0], out_point[1], True])
                                else:
                                    if [cord[0], out_point[1], True] in update_laser2:
                                        update_laser2.append([cord[0], out_point[0], True])
                                    else:
                                        update_laser2.append([cord[0], out_point[0], True])
                                        update_laser2.append([cord[0], out_point[1], True])
                    else:
                        pass
            if candidate2 != 'none':
                if candidate3 != 'none' and out_point3 != 'none':
                    mid[cord[0]] = [candidate3, out_point3, True]
                    lll = Laser(cord[0], candidate2)
                    if lll.between_two_point_or_not(candidate2, candidate3) is True:
                        pass
                    else:
                        mid[(candidate2, out_point2[0])] = [candidate2, out_point2[0], True]
                        mid[(candidate2, out_point2[1])] = [candidate2, out_point2[1], True]
                else:
                    mid[(candidate2, out_point2[0])] = [candidate2, out_point2[0], True]
                    mid[(candidate2, out_point2[1])] = [candidate2, out_point2[1], True]
            else:
                if candidate3 != 'none' and out_point3 != 'none':
                    mid[cord[0]] = [candidate3, out_point3, True]
                else:
                    pass
        for cord in update_laser:
            if cord[2] is False:
                if cord in result:
                    pass
                else:
                    if cord[1] == 'none':
                        pass
                    else:
                        result.append(cord)
            else:
                if cord in update_laser2:
                    pass
                else:
                    if cord in contain:
                        pass
                    else:
                        update_laser2.append(cord)
        # print(update_laser2, type(update_laser2))
        # print(mid)
        # print(update_laser2)
        length = len(result)
        if length in stop:
            count += 1
        else:
            count = 0
            stop.append(length)
        if len(mid) == 0:
            pass
        else:
            for i in mid:
                update_laser2.append(mid[i])
        for j in update_laser:
            if j[1] == 'none' and j in update_laser2:
                update_laser2.remove(j)
            else:
                pass

        update_laser3 = copy.deepcopy(update_laser2)
        for i in result:
            l = Laser(i[0], i[1])
            k, b = l.line()
            for j in update_laser2:
                ll = Laser(j[0], j[1])
                k2, b2 = ll.line()
                if k == k2 and b == b2 and l.between_two_point_or_not(i[1], j[0]) is True and vector_in_same_direction(i, j) is True:
                    if j in update_laser3:
                        update_laser3.remove(j)
                    else:
                        pass
                elif k == k2 and b == b2 and l.between_two_point_or_not(i[0], j[1]) is True and vector_in_same_direction(i, j) is True:
                    if j in update_laser3:
                        update_laser3.remove(j)
                    else:
                        pass
        laser2 = update_laser3
        # print(update_laser3)
        # print(result)
    # #
    # print(result)
    for cord in result:
        l = Laser(cord[0], cord[1])
        for i in goal:
            if operator.eq(cord[0], i) is True:
                if i in target:
                    target.remove(i)
                else:
                    pass
            else:
                pass
            if cord[2] == False:
                if l.laser_intersect_or_not(i) is True and l.between_two_point_or_not(cord[1], i) is True:
                    if i in target:
                        target.remove(i)
                    else:
                        pass
                else:
                    pass
            else:
                if l.laser_intersect_or_not(i) is True:
                    if i in target:
                        target.remove(i)
                    else:
                        pass
                else:
                    pass
            # print(target)
    if len(target) == 0:
        return True
    else:
        return False

def vector_in_same_direction(vector1, vector2):
    aa = (vector1[1][0] - vector1[0][0], vector1[1][1] - vector1[0][1])
    bb = (vector2[1][0] - vector2[0][0], vector2[1][1] - vector2[0][1])
    a = aa[0] / bb[0]
    b = aa[1] / bb[1]
    if a == b and a > 0:
        return True
    else:
        return False

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
    Input_file("bff")
    # b = Block((3, 3))
    # b2 = Block((1, 3))
    # b3 = Block((0, 2))
    # b4 = Block((2, 4))
    # b5 = Block((1, 1))
    # block_class = [(b, 'A'), (b2, 'A'), (b3, 'A'), (b4, 'A'), (b5, 'A')]
    # print(find_solution(block_class, [[(7, 2), (6, 3), True]], [(3, 4), (7, 4), (5, 8)]))
    # b = Block((1, 0))
    # b2 = Block((2, 0))
    # b3 = Block((0, 1))
    # block_class = [(b, 'B'), (b2, 'B'), (b3, 'B')]
    # print(find_solution(block_class, [[(3, 0), (2, 1), True], [(1, 6), (2, 5), True], [(3, 6), (2, 5), True], [(4, 3), (5, 2), True]], [(0, 3), (6, 1)]))
    # b = Block((0, 2))
    # b2 = Block((3, 1))
    # b3 = Block((2, 0))
    # block_class = [(b, 'A'), (b2, 'A'), (b3, 'C')]
    # print(find_solution(block_class, [[(2, 7), (3, 6), True]], [(3, 0), (4, 3), (2, 5), (4, 7)]))
    # print(vector_in_same_direction([(2, 3), (3, 2), True], [(3, 2), (2, 3), True]))
    # b = Block((1, 2))
    # b2 = Block((2, 0))
    # b3 = Block((0, 0))
    # b4 = Block((2, 2))
    # b5 = Block((1, 0))
    # block_class = [(b, 'A'), (b2, 'A'), (b3, 'A'), (b4, 'C'), (b5, 'B')]
    # # print(b4.refract((4, 5), (3, 4)))
    # print(find_solution(block_class, [[(4, 5), (3, 4), True]], [(1, 2), (6, 3)]))
    # for i in a:
    #     print(a[i])
    end = time.time()
    print(end - start)


