'''
Author: Zichen Liu for all code and comment

This file contains a solver for Lazor game
and write the solution back to a txt file
'''
import os
import numpy as np
import itertools
import time
import copy
import operator
import multiprocessing
import numba


def MAIN(path):
    '''
    This is the main function for the solver, take in the folder path and solve each level's .bff files in the folder.
    this main function use multiprocess to speed up the solving process.
    :param path: the path for the folder that contain the bff file.
    :return: no returns. just print out that write to file succeed.
    '''
    name_list = []
    file_list = []
    # walk through the directory and only append .bff file
    for fpathe, dirs, i in os.walk(path):
        for ff in i:
            a = ff.split('.')
            if a[1] == 'bff':
                name_list.append(a[0])
                file_list.append(os.path.join(fpathe, ff))
            else:
                continue
    # solve all the bff file in the folder in a loop
    for file in file_list:
        NAME = name_list[file_list.index(file)]
        print('Solving %s .... ' % NAME)
        f = open(file)
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
        # find all the possible position in the grid
        for i in range(len(grid)):
            for ii in range(len(grid[0])):
                if grid[i][ii] != 'o':
                    continue
                else:
                    possible_position.append((ii, i))
        # if there is a fixed block in the grid find the fixed grid position
        fixed = fix_block(grid)
        # initial the fixed block with its position
        fixed_class = []
        if fixed == []:
            pass
        else:
            for i in fixed:
                fixed_class.append((Block(i[0]), i[1]))
        # count all movable block number
        block_total = 0
        for i in block:
            block_total += block[i]
        # contain all possible combination in a list
        combination = list(itertools.combinations(possible_position, block_total))
        # count the cpu number
        core_num = multiprocessing.cpu_count()
        segment = len(combination) // core_num
        # cut all possible combination in to core number's pieces
        combination_segment = []
        for cores in range(core_num):
            combination_segment.append(combination[cores * segment:(cores + 1) * segment])
        combination_segment.append(combination[core_num * segment:len(combination)])
        # queue is used for the communication between parent process and child process
        queue = multiprocessing.Queue(1)
        result = []
        # start the multiprocessing
        for count_process in combination_segment:
            p = multiprocessing.Process(target=worker, args=(queue, count_process, block, block_total, fixed_class, laser, points))
            p.start()
            result.append(p)
        final_result = queue.get()
        # if the queue is empty kill all child process
        if queue.empty() is True:
            for ppp in result:
                ppp.terminate()
        else:
            pass
        p.join()
        # out put the final result to a text file
        outs = output(file, NAME, final_result[1], grid)
        print(outs)

def output(input_file_path, name, result, grid):
    '''
    This function take in the bff file path, the name for the file name, the final solution for this file and the grid
    for this level.
    :param input_file_path: the path for the the bll file.
    :param name: the name for the bff file.
    :param result: the final result for the file. list contain several tuple
    :param grid: the list for the map of this file. list contain list
    :return: return a string tells the out put to a file has done
    '''
    split = input_file_path.split('.')
    out_file_path = split[0] + '_solution.txt'
    f2 = open(out_file_path, "w")
    f2.write('Solution for %s: \n' % name)
    for solution in result:
        cord = solution[0]
        grid[cord[1]][cord[0]] = solution[1]
    for i in grid:
        for j in i:
            f2.write(j + '\t')
        f2.write('\n')
    return 'Solution is in %s' % out_file_path

def worker(queue, combination, block, block_total, fixed_class, laser, points):
    '''
    This is the function for the multiprocess. This function is assigned to a CPU core.
    :param queue: this is the queue created by parent process, to gain the run status of this subprocess. object
    :param combination: this is the list for combination of a specific level. list contain several tuple
    :param block: this is a dic that the key is the block kind and the value is the number of the block. dic
    :param block_total: the total number of all movable block. int
    :param fixed_class: this is a list contain the fixed block after initial through Block class. list contain several
     tuple and each tuple contain object and string
    :param laser: this is a list contain the laser origin and direction. list
    :param points: this is a list contain the goal for the laser. list
    :return: return the solution for the level and bool type. if there is a solution the result is True vice versa.
    '''
    result = False
    solution = []
    for jj in combination:
        result, solution = sub_process(jj, block, block_total, fixed_class, laser, points)
        if result is True:
            # if there is a solution, put the solution to parent queue
            queue.put((result, solution))
            break
        else:
            continue
    return result, solution

def sub_process(i, block, block_total, fixed_class, laser, points):
    '''
    this is the sub process for the worker function.
    :param i: one possible combination for block position. tuple
    :param block: this is a dic that the key is the block kind and the value is the number of the block. dic
    :param block_total: the total number of all movable block. int
    :param fixed_class: this is a list contain the fixed block after initial through Block class. list contain several
    tuple and each tuple contain object and string
    :param laser: this is a list contain the laser origin and direction. list
    :param points: this is a list contain the goal for the laser. list
    :return: return the solution for the level and bool type. if there is a solution the result is True vice versa.
    '''
    # this is used to break for loop.
    b = 0
    # if there are two kind of block that can move
    if len(block) == 2:
        keys = list(block.keys())
        # get the number for each kind block
        num1 = block.get(keys[0])
        num2 = block.get(keys[1])
        for ii in itertools.combinations(i, num1):
            block_class = []
            # this is used to put in the solution
            cllll = []
            possible_block_position = list(ii)
            cross = list(set(i) ^ set(ii))
            # initial the block with the position and put the object in a list
            for j in range(num1):
                block_class.append((Block(possible_block_position[-1]), keys[0]))
                cllll.append((possible_block_position[-1], keys[0]))
                possible_block_position.pop()
            for k in range(num2):
                block_class.append((Block(cross[-1]), keys[1]))
                cllll.append((cross[-1], keys[1]))
                cross.pop()

            block_class.extend(fixed_class)
            # solve one possible position at a time
            a = find_solution(block_class, laser, points)
            if a is True:
                return a, cllll
            else:
                continue
    # if there are three kind of block that can move
    elif len(block) == 3:
        num1 = block.get('A')
        num2 = block.get('B')
        num3 = block.get('C')
        for ii in itertools.combinations(i, num1):
            block_class = []
            cllll = []
            possible_block_position = list(ii)
            cross = list(set(i) ^ set(ii))
            for j in range(num1):
                block_class.append((Block(possible_block_position[-1]), 'A'))
                cllll.append((possible_block_position[-1], 'A'))
                possible_block_position.pop()
            for iii in itertools.combinations(cross, num2):
                cross2 = list(set(cross) ^ set(iii))
                possible_block_position2 = list(iii)
                for k in range(num2):
                    block_class.append((Block(possible_block_position2[-1]), 'B'))
                    cllll.append((possible_block_position2[-1], 'B'))
                    possible_block_position2.pop()
                for kk in range(num3):
                    block_class.append((Block(cross2[-1]), 'C'))
                    cllll.append((cross2[-1], 'C'))
                    cross2.pop()
                    # solve one possible position at a time
                    a = find_solution(block_class, laser, points)
                    if a is True:
                        b = 2
                        break
                    else:
                        continue
            if b == 2:
                return a, cllll
            else:
                pass
    # if there is one kind of block that can move
    elif len(block) == 1:
        block_class = []

        cllll = []
        possible_block_position = list(i)
        for ii in range(block_total):
            block_class.append((Block(possible_block_position[-1]), list(block.keys())[0]))
            cllll.append((possible_block_position[-1], list(block.keys())[0]))
            possible_block_position.pop()
        block_class.extend(fixed_class)
        # solve one possible position at a time
        a = find_solution(block_class, laser, points)
        if a is True:
            return a, cllll
        else:
            pass
    else:
        cllll = []
        pass
    return False, []

def find_solution(block_class, laser, goal):
    '''
    This is the main function for finding solution algorithm. Take in the object list after initialization, the laser
    coordinate and the goal for the laser.
    :param block_class: the object list after initialization with corresponding position. list contain several tuple
     and each tuple contain object and string
    :param laser: a list contain each laser origin and direction. list
    :param goal: contain the goal for the laser. list
    :return: return the solution for the level and bool type. if there is a solution the result is True vice versa.
    '''
    target = copy.deepcopy(goal)
    laser2 = copy.deepcopy(laser)
    count = 0
    stop = []
    contain = []
    result = []
    update_laser3 = []
    # create a loop to trace the laser
    while True:
        # if the length for result is not changing then break out the loop.
        if count > 1:
            result.extend(update_laser3)
            break
        else:
            pass
        # this is use to contain the intersection point between the laser and the block
        possible_candidate = set()
        # this is used to update the laser coordinate
        update_laser = copy.deepcopy(laser2)
        # this is used to contain the out going laser, reflect or refract.
        mid = {}
        # this is used to contain the out going laser with True flag on it
        update_laser2 = []
        # trace each leaser
        for cord in laser2:
            distance = float('inf')
            candidate2 = 'none'
            out_point2 = 'none'
            candidate3 = 'none'
            out_point3 = 'none'
            # find the intersection on each block
            for block in block_class:
                if block[1] == 'A':
                    _, candidate, out_point = block[0].reflect(cord[0], cord[1])
                    if candidate != 'none':
                        possible_candidate.add((candidate, out_point, 'A'))
                        # find the nearest reflect block or opaque block for a specific laser
                        update_dis = np.linalg.norm(np.array(candidate) - np.array(cord[0]))
                        if update_dis < distance:
                            distance = update_dis
                            candidate3 = candidate
                            out_point3 = out_point
                            if cord[0] != candidate:
                                update_laser[laser2.index(cord)] = [cord[0], candidate, False]
                            else:
                                update_laser[laser2.index(cord)] = [cord[0], out_point, True]
                                if cord in contain:
                                    pass
                                else:
                                    contain.append(cord)
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
            # keep track the laser that goes out
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
        # separate the update laser by its flag
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
        # keep track the length of the result list
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
        # get rid of the repeat laser and the laser that is piercing through.
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
    # goe over all the laser in the result if there is a laser intersect the goal then remove the goal
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
    # if all goal is removed then return true
    if len(target) == 0:
        return True
    else:
        return False

def vector_in_same_direction(vector1, vector2):
    '''
    this is the function to determin two vector is in the same direction or not. the two vector is represent by the start
    and end point coordinate.
    :param vector1: a tuple contain the start and end point coordinate. tuple
    :param vector2: a tuple contain the start and end point coordinate. tuple
    :return: if in same direction then return true else return false.
    '''
    aa = (vector1[1][0] - vector1[0][0], vector1[1][1] - vector1[0][1])
    bb = (vector2[1][0] - vector2[0][0], vector2[1][1] - vector2[0][1])
    a = aa[0] / bb[0]
    b = aa[1] / bb[1]
    if a == b and a > 0:
        return True
    else:
        return False

def fix_block(grid):
    '''
    find fixed block in the grid.
    :param grid: the map for each level. list
    :return: returns the fixed block position. list
    '''
    position_category = []
    for i in range(len(grid)):
        for ii in range(len(grid[0])):
            if grid[i][ii].isupper() is True:
                position_category.append([(ii, i), grid[i][ii]])
            else:
                continue
    return position_category



class Laser(object):
    '''
    This is the class for the laser.
    '''
    def __init__(self, position1, position2):
        '''
        initial the laser with its origin and direction.
        :param position1: the origin point for the laser. tuple
        :param position2: the direction point for the laser. tuple
        '''
        self.position1 = position1
        self.position2 = position2
    def line(self):
        '''
        this is used to calculate the slop and the intersection for the line of the laser.
        :return: return the slop and the intersection of the line of the laser.
        '''
        k = (self.position1[1] - self.position2[1]) / (self.position1[0] - self.position2[0])
        b = self.position1[1] - k * self.position1[0]
        return k, b
    def laser_intersect_or_not(self, query):
        '''
        this is use to calculate if the query point can be intersected by the laser.
        :param query: the point coordinate you want to check. tuple
        :return: if the query is on the laser return True else return false.
        '''
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
        '''
        this the function used to check the query point is fall between laser origin point and candidate point.
        :param candidate: the end point for the line segment. tuple
        :param query: the point you want to check. tuple
        :return: if the query fall between the two point retrun true else return false.
        '''
        self.query = query
        self.candidate = candidate
        x_cord = [self.candidate[0], self.position1[0]]
        y_cord = [self.candidate[1], self.position1[1]]
        if self.query[0] >= min(x_cord) and self.query[1] >= min(y_cord) and self.query[0] <= max(x_cord) and self.query[1] <= max(y_cord):
            return True
        else:
            return False






class Block(object):
    '''
    This is the class for the three kind of blocks.
    '''
    def __init__(self, block_position):
        '''
        initial the block with its actual position.
        :param block_position: the position where the block is in. tuple
        '''
        self.block_position = block_position
    def intersect_point(self):
        '''
        this is used to return the possible intersection point and the intersection surface on the block.
        :return: return the possible intersection point and the intersection surface.
        '''
        x_cord = 2 * self.block_position[0] + 1
        y_cord = 2 * self.block_position[1] + 1
        intersect_surface = {(x_cord, y_cord - 1): 'up', (x_cord, y_cord + 1): 'down',
                          (x_cord - 1, y_cord): 'left', (x_cord + 1, y_cord): 'right'}
        intersect_point = [(x_cord, y_cord - 1), (x_cord, y_cord + 1), (x_cord - 1, y_cord), (x_cord + 1, y_cord)]
        return intersect_point, intersect_surface
    def reflect(self, laser_origin_point, incoming_laser_point):
        '''
        this is used to calculate the reflect block.
        :param laser_origin_point: the origin point for the laser. tuple
        :param incoming_laser_point: the direction point for the laser. tuple
        :return: return the intersection point where laser intersect, the outgoing laser slop and line intersection
        and the outgoing laser laser direction point.
        '''
        self.k, self.b = Laser(laser_origin_point, incoming_laser_point).line()
        self.incoming_laser_point = incoming_laser_point
        self.origin_point = laser_origin_point
        intersect_point, intersect_surface = Block.intersect_point(self)
        min_distance = float('inf')
        candidate = 'none'
        out_point = 'none'
        laser_in_block = copy.deepcopy(intersect_point)
        # determine if the laser can shoot on the block
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
        '''
        this is used to calculate the opaque block.
        :param laser_origin_point: the origin point for the laser. tuple
        :param incoming_laser_point: the direction point for the laser. tuple
        :return: return the intersection point where laser intersect. The slop and intersection of the outgoing line is
        set to 'none'. The outgoing direction is set to 'none'
        '''
        self.k, self.b = Laser(laser_origin_point, incoming_laser_point).line()
        self.incoming_laser_point = incoming_laser_point
        self.origin_point = laser_origin_point
        intersect_point, intersect_surface = Block.intersect_point(self)
        min_distance = float('inf')
        candidate = 'none'
        laser_in_block = copy.deepcopy(intersect_point)
        # determine if the laser can shoot on the block.
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
        '''
        this is used to calculated the refract block.
        :param laser_origin_point: the origin point for the laser. tuple
        :param incoming_laser_point: the direction point for the laser. tuple
        :return: return the intersection point where laser intersect, the outgoing laser slop and line intersection
        and the outgoing laser laser direction point. the origin laser slop and line intersection and the origin laser
        direction point.
        '''
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
        # determine if the laser can shoot on the block.
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
    MAIN('bff')
    end = time.time()
    print('Total run time is %0.2f Seconds' % (end - start))