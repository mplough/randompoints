# Generate random points

## Setup

1. `pipenv install`
1. `pipenv shell`

## Examples

All units are in millimeters.

Make a 11x17 plot:
```bash
python random_points_quadtree.py \
    --out-filename points.csv \
    --plot-filename plot.pdf \
    --max-x 279.4 \
    --max-y 355.6 \
    --marker-size 0.4 \
    --min-dist 0.5 \
    --n-points 150000
```
