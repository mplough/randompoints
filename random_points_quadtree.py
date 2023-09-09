# Generates random points that are a at least a minimum distance apart.  Uses
# rejection sampling.  The rejection is performed with the aid of a quadtree,
# which greatly increases the speed over the naive version.  The run time
# complexity is O(n log n), rather than O(n^2).

import csv
import random
from math import sqrt
from pathlib import Path

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


# axis-aligned bounding box
class AABB:
    def __init__(self, left, bottom, right, top):
        self.lower_left = Point(left, bottom)
        self.upper_right = Point(right, top)

    def contains(self, point):
        if self.lower_left.x > point.x or point.x > self.upper_right.x:
            return False
        if self.lower_left.y > point.y or point.y > self.upper_right.y:
            return False
        return True

    def intersects(self, aabb):
        if self.lower_left.x > aabb.upper_right.x:
            return False
        if aabb.lower_left.x > self.upper_right.x:
            return False
        if self.lower_left.y > aabb.upper_right.y:
            return False
        if aabb.lower_left.y > self.upper_right.y:
            return False
        return True

    def __str__(self):
        return f"{self.lower_left} to {self.upper_right}"

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
        x0 = self.boundary.lower_left.x
        y0 = self.boundary.lower_left.y
        x2 = self.boundary.upper_right.x
        y2 = self.boundary.upper_right.y
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

        raise ValueError("Should never reach here")

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

def is_acceptable(candidate, tree, min_dist):
    aabb = AABB(candidate.x - min_dist,
            candidate.y - min_dist,
            candidate.x + min_dist,
            candidate.y + min_dist)
    points = tree.query(aabb)

    for p in points:
        if candidate.distance_to(p) < min_dist:
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
    boundary = AABB(min_x, min_y, max_x, max_y)
    tree = QuadtreeNode(boundary)

    while tries < max_tries and len(points) < n_points:
        if tries % 10_000 == 0:
            print(f"tried {tries}, have {len(points)} / {n_points}")
        x = random.uniform(min_x, max_x)
        y = random.uniform(min_y, max_y)

        p = Point(x,y)
        tries += 1

        if is_acceptable(p, tree, min_dist):
            points.append(p)
            tree.insert(p)
        else:
            continue

    return points


def write_points(points, filename):
    print(f"Writing out {filename} ...")
    with open(filename, "w") as f:
        out = csv.writer(f)
        out.writerow(("x", "y"))
        for p in points:
            out.writerow((p.x, p.y))


def inches_from_mm(mm):
    return 1/25.4 * mm

def points_from_mm(mm):
    return 72 * inches_from_mm(mm)

def make_plot(
*,
    points: list[Point],
    filename: Path,
    min_x: float,
    max_x: float,
    min_y: float,
    max_y: float,
    marker_size: float = 1,
):
    print(f"Writing plot to {filename} ...")

    import matplotlib.pyplot as plt
    from mpl_toolkits.axes_grid1 import Divider, Size

    # axes with a fixed physical size
    # see https://matplotlib.org/stable/gallery/axes_grid1/demo_fixed_size_axes.html

    x_inches = inches_from_mm(max_x - min_x)
    y_inches = inches_from_mm(max_y - min_y)

    fig = plt.figure(figsize=(x_inches, y_inches))

    # The first items are for padding and the second items are for the axes.
    # sizes are in inch.
    h = [Size.Fixed(0), Size.Fixed(x_inches)]
    v = [Size.Fixed(0), Size.Fixed(y_inches)]
    divider = Divider(fig, (0, 0, 1, 1), h, v, aspect=False)

    # The width and height of the rectangle are ignored.
    ax = fig.add_axes(divider.get_position(),
                      axes_locator=divider.new_locator(nx=1, ny=1))

    # markers: https://matplotlib.org/stable/gallery/lines_bars_and_markers/marker_reference.html#filled-markers
    ax.scatter(
        x=[p.x for p in points],
        y=[p.y for p in points],
        s=points_from_mm(marker_size)**2,
        c="black",
        marker="o",
        edgecolor="none",
    )

    ax.set(
        xlim=(min_x, max_x),
        ylim=(min_y, max_y),
    )

    fig.patch.set_visible(False)
    ax.axis('off')

    plt.savefig(filename, bbox_inches="tight", pad_inches = 0)


def test():
    min_x = 0
    max_x = 100
    min_y = 0
    max_y = 100

    boundary = AABB(min_x, min_y, max_x, max_y)
    tree = QuadtreeNode(boundary)

    tree.insert(Point(4,4))

    print(tree.boundary)
    for p in tree.query(boundary):
        print(p)


def n_points_from_density(x, y, points_per_100x100: float):
    area = x * y
    unit_area = 100 * 100
    return int(points_per_100x100 * area / unit_area)


@click.command
@click.option(
    "--points-filename",
    type=click_pathlib.Path(exists=False),
)
@click.option(
    "--n-points",
    type=int,
)
@click.option(
    "--points-per-100x100",
    type=int,
)
@click.option(
    "--min-dist",
    type=float,
    default=1.0
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
@click.option(
    "--plot-filename",
    type=click_pathlib.Path(exists=False),
)
@click.option(
    "--marker-size",
    type=float,
    default=1.0
)
def click_main(
    points_filename,
    min_dist,
    n_points,
    points_per_100x100,
    min_x,
    max_x,
    min_y,
    max_y,
    random_seed,
    plot_filename,
    marker_size,
):
    if points_filename is None and plot_filename is None:
        raise ValueError("No output formats specified")

    if random_seed is not None:
        random.seed(random_seed)

    if points_per_100x100 is not None:
        n_points = n_points_from_density(
            max_x - min_x,
            max_y - min_y,
            points_per_100x100
        )
    if n_points is None:
        raise ValueError("number of points was not specified")

    points = generate_points(
        min_dist=min_dist,
        n_points=n_points,
        min_x=min_x,
        max_x=max_x,
        min_y=min_y,
        max_y=max_y,
    )

    if points_filename is not None:
        write_points(points, points_filename)

    if plot_filename is not None:
        make_plot(
            points=points,
            filename=plot_filename,
            min_x=min_x,
            max_x=max_x,
            min_y=min_y,
            max_y=max_y,
            marker_size=marker_size,
        )


if __name__ == "__main__":
    click_main()
    #test()
