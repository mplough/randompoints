# Generates random points that are a at least a minimum distance apart.
# Uses rejection sampling.  Currently the rejection is performed naively.
# Each candidate point is checked against all previously accepted points,
# leading to a run time complexity of O(n^2).
#
# See random_points_quadtree.py for an algorithmically faster implementation.
#
# There are probably better ways to do this than rejection sampling.
# I'd like to look into those ways at some point.

import csv
import random
from math import sqrt

import click
import click_pathlib

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance_to(self, point):
        return sqrt(self.squared_distance_to(point))

    def squared_distance_to(self, point):
        dx = self.x - point.x
        dy = self.y - point.y
        distance_2 = dx**2 + dy**2
        return distance_2

    def __str__(self):
        return f"({self.x}, {self.y})"


def is_acceptable(candidate, points, min_dist):
    """Brute force checks every point."""
    for p in points:
        if candidate.squared_distance_to(p) < min_dist*2:
            return False
    return True


def generate_points(
    *,
    min_dist: float,
    n_points = 10_000,
    min_x: float = 0,
    max_x: float = 100,
    min_y: float = 0,
    max_y: float = 100,
):
    # setup
    tries = 0
    max_tries = 30 * n_points
    points = []

    while tries < max_tries and len(points) < n_points:
        if tries % (max_tries / 100) == 0:
            print(f"tried {tries}, have {len(points)} / {n_points}")
        x = random.uniform(min_x, max_x)
        y = random.uniform(min_y, max_y)

        p = Point(x,y)
        tries += 1

        if is_acceptable(p, points, min_dist):
            points.append(p)
        else:
            continue

    return points


def write_points(points, out_filename):
    print(f"Writing out {out_filename} ...")
    with open(out_filename, "w") as f:
        out = csv.writer(f)
        out.writerow(("x", "y"))
        for p in points:
            out.writerow((p.x, p.y))


@click.command
@click.option(
    "--out-filename",
    required=True,
    type=click_pathlib.Path(exists=False),
)
@click.option(
    "--n-points",
    type=int,
    default=10_000,
)
@click.option(
    "--min-dist",
    required=True,
    type=float,
)
@click.option(
    "--min-x",
    type=float,
    default=0.0
)
@click.option(
    "--max-x",
    type=float,
    default=100.0
)
@click.option(
    "--min-y",
    type=float,
    default=0.0
)
@click.option(
    "--max-y",
    type=float,
    default=100.0
)
@click.option(
    "--random-seed",
    type=int,
)
def click_main(
    out_filename,
    min_dist,
    n_points,
    min_x,
    max_x,
    min_y,
    max_y,
    random_seed
):
    if random_seed is not None:
        random.seed(random_seed)

    points = generate_points(
        min_dist=min_dist,
        n_points=n_points,
        min_x=min_x,
        max_x=max_x,
        min_y=min_y,
        max_y=max_y,
    )
    write_points(points, out_filename)


if __name__ == "__main__":
    click_main()
