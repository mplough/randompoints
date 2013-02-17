# 
# randomPoints.py
#
# Matthew Plough
# February 14, 2013
#
# Generates random points that are a at least a minimum distance apart.
# Uses rejection sampling.  Currently the rejection is performed naively.
# Each candidate point is checked against all previously accepted points,
# leading to a run time complexity of O(n^2).  I would like to move to
# a quadtree implementation, which will take the run time complexity 
# down to O(n log n).
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

def isAcceptable(candidate, points, minDist):

    # This brute force checks every point.
    # TODO Want to do a quadtree implementation later.

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

    while tries < maxTries and len(points) < nPoints:
        if tries % (maxTries / 100) == 0:
            print "tried %d, have %d / %d" % (tries, len(points), nPoints)
        x = random.uniform(minX, maxX)
        y = random.uniform(minY, maxY)

        p = Point(x,y)
        tries += 1

        if isAcceptable(p, points, minDist):
            points.append(p)
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

if __name__ == "__main__":
    main(sys.argv)
