# 
# randomPoints_quadtree.py
#
# Matthew Plough
# February 17, 2013
#
# Generates random points that are a at least a minimum distance apart.  Uses
# rejection sampling.  The rejection is performed with the aid of a quadtree,
# which greatly increases the speed over the naive version.  The run time
# complexity is O(n log n), rather than O(n^2).
#
# I don't have Matlab on this machine, so I've been doing the plots in Excel.
# I'd like to learn how to use R.  Why?
# 1) I can use it to script the plotting operation
# 2) I can probably use it to implement this program
# 3) I can use it to do statistical stuff in general
#
# Also, there are probably better ways to do this than rejection sampling,
# and I'd like to look into those ways.

import csv
import sys
from math import *
import random

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distanceTo(self, point):
        dx = self.x - point.x
        dy = self.y - point.y
        distance = sqrt(dx*dx + dy*dy)
        return distance

    def __str__(self):
        return "(%f, %f)" % (self.x, self.y)

# axis-aligned bounding box
class AABB:
    def __init__(self, left, bottom, right, top):
        self.lowerLeft = Point(left, bottom)
        self.upperRight = Point(right, top)

    def contains(self, point):
        if self.lowerLeft.x > point.x or point.x > self.upperRight.x:
            return False
        if self.lowerLeft.y > point.y or point.y > self.upperRight.y:
            return False
        return True

    def intersects(self, aabb):
        if self.lowerLeft.x > aabb.upperRight.x:
            return False
        if aabb.lowerLeft.x > self.upperRight.x:
            return False
        if self.lowerLeft.y > aabb.upperRight.y:
            return False
        if aabb.lowerLeft.y > self.upperRight.y:
            return False
        return True

    def __str__(self):
        return "%s to %s" % (self.lowerLeft, self.upperRight)

class QuadtreeNode:
    def __init__(self, boundary):
        self.ne = None
        self.nw = None
        self.sw = None
        self.se = None

        self.boundary = boundary

        self.points = []
        self.MAX_POINTS = 4

    def subdivide(self):
        x0 = self.boundary.lowerLeft.x
        y0 = self.boundary.lowerLeft.y
        x2 = self.boundary.upperRight.x
        y2 = self.boundary.upperRight.y
        x1 = (x0 + x2) / 2.0
        y1 = (y0 + y2) / 2.0

        self.ne = QuadtreeNode(AABB(x1, y1, x2, y2))
        self.nw = QuadtreeNode(AABB(x0, y1, x1, y2))
        self.sw = QuadtreeNode(AABB(x0, y0, x1, y1))
        self.se = QuadtreeNode(AABB(x1, y0, x2, y1))

    def insert(self, p):
        if self.boundary.contains(p) == False:
            return False

        if len(self.points) < self.MAX_POINTS:
            self.points.append(p)
            return True

        if self.ne == None:
            self.subdivide()

        if self.ne.insert(p):
            return True
        if self.nw.insert(p):
            return True
        if self.se.insert(p):
            return True
        if self.sw.insert(p):
            return True

        # should never reach here
        print "WTF!!!!"
        return False
    
    def query(self, aabb):
        if self.boundary.intersects(aabb) == False:
            return []

        points = []
        for p in self.points:
            if aabb.contains(p):
                points.append(p)

        if self.ne == None:
            return points

        points.extend(self.ne.query(aabb))
        points.extend(self.nw.query(aabb))
        points.extend(self.se.query(aabb))
        points.extend(self.sw.query(aabb))

        return points

def isAcceptable(candidate, tree, minDist):
    aabb = AABB(candidate.x - minDist, 
            candidate.y - minDist, 
            candidate.x + minDist, 
            candidate.y + minDist)
    points = tree.query(aabb)

    for p in points:
        if candidate.distanceTo(p) < minDist:
            return False

    return True

def generatePoints(minDist):
    # parameters -- TODO makes these arguments
    nPoints = 10000
    #minDist = 5
    minX = 0
    maxX = 100
    minY = 0
    maxY = 100

    # setup
    tries = 0
    maxTries = 30*nPoints
    points = []
    boundary = AABB(minX, minY, maxX, maxY)
    tree = QuadtreeNode(boundary)

    while tries < maxTries and len(points) < nPoints:
        if tries % (maxTries / 100) == 0:
            print "tried %d, have %d / %d" % (tries, len(points), nPoints)
        x = random.uniform(minX, maxX)
        y = random.uniform(minY, maxY)

        p = Point(x,y)
        tries += 1

        if isAcceptable(p, tree, minDist):
            points.append(p)
            tree.insert(p)
        else:
            continue

    return points

def writePoints(points, outFileName):
    f = open(outFileName, "wb")
    out = csv.writer(f)

    for p in points:
        out.writerow((p.x, p.y))

    f.close()

def main(argv):
    outFileName = argv[1] 
    minDist = float(argv[2])

    random.seed(0)
    points = generatePoints(minDist)
    writePoints(points, outFileName)

def test():
    minX = 0
    maxX = 100
    minY = 0
    maxY = 100

    boundary = AABB(minX, minY, maxX, maxY)
    tree = QuadtreeNode(boundary)

    tree.insert(Point(4,4))

    print tree.boundary
    for p in tree.query(boundary):
        print p

if __name__ == "__main__":
    main(sys.argv)
    #test()
