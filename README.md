# Generate random points

# Overview

`random_points.py` uses rejection sampling to generate random points that are a
at least a minimum distance apart.  The rejection is performed naively: Each
candidate point is checked against all previously accepted points, leading to a
run time complexity of O(n^2), where n is the number of points generated.

`random_points_quadtree` speeds up the sampling by using a quadtree to store
previously generated points.  This data structure improves run time complexity
to O(n log n).

Next up: stratified sampling.  See https://inst.eecs.berkeley.edu/~cs294-13/fa09/lectures/course29sig01.pdf and https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=4b29674656bbf4067f23f0c24fe1b2e7ae198d7f

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
