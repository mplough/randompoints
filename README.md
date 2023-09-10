# Generate random points

# Overview

`random_points.py` uses rejection sampling to generate random points that are a
at least a minimum distance apart.  The rejection is performed naively: Each
candidate point is checked against all previously accepted points, leading to a
run time complexity of O(n^2), where n is the number of points generated.

`random_points_quadtree` speeds up the sampling by using a quadtree to store
previously generated points.  This data structure improves run time complexity
to O(n log n).

# Use

## Setup

1. `pipenv install`
1. `pipenv shell`

## Examples

All units are in millimeters.

Make an 8.5 x 11 chart.

```bash
python random_points_quadtree.py \
    --points-filename points.csv \
    --plot-filename plot.pdf \
    --max-x 215.9 \
    --max-y 279.4 \
    --marker-size 0.4 \
    --min-dist 0.4 \
    --points-per-100x100 30000
```

# Next areas to explore

## Quasi-Monte Carlo (QMC) methods

* https://www.scratchapixel.com/lessons/mathematics-physics-for-computer-graphics/monte-carlo-methods-in-practice/introduction-quasi-monte-carlo.html

## Poisson disc sampling

* https://www.jasondavies.com/poisson-disc/
* O(n) algorithm for this. https://www.cs.ubc.ca/~rbridson/docs/bridson-siggraph07-poissondisk.pdf
* Original Cook paper.  What he calls "jittered sampling" is now normally called "stratified sampling". http://www.cs.cmu.edu/afs/cs/academic/class/15462-s15/www/lec_slides/p51-cook.pdf

## Blue noise sampling

* https://blog.demofox.org/2017/10/20/generating-blue-noise-sample-points-with-mitchells-best-candidate-algorithm/
* https://blog.demofox.org/2017/05/29/when-random-numbers-are-too-random-low-discrepancy-sequences/
