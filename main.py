import csv
from pprint import pprint
from decimal import Decimal
import matplotlib.pyplot as plt
from PIL import Image

count = 185
dot_size = 60  
limits = {'x': [Decimal('34.376640108654158'), Decimal('35.774892331016304')],
          'y': [Decimal('29.529264258238982'), Decimal('33.283289929186935')]}
deltas = [limits["x"][1] - limits["x"][0], limits["y"][1] - limits["y"][0]]


def calc_limits(r):
    limits = {"x": [Decimal(100), Decimal(0)], "y": [Decimal(100), Decimal(0)]}
    first = True
    for i in r:

        if first:
            first = False
            continue

        pos = i[1].split(" ")
        x = Decimal(pos[1].lstrip("("))
        y = Decimal(pos[2].rstrip(")"))
        # print(x, y)

        if x < limits["x"][0]:
            limits["x"][0] = x
        elif x > limits["x"][1]:
            limits["x"][1] = x

        if y < limits["y"][0]:
            limits["y"][0] = y
        elif y > limits["y"][1]:
            limits["y"][1] = y

    return limits


def get_points():
    points = []
    with open(r"<Original Coordinates>.csv", "r") as f:
        r = csv.reader(f)

        first = True
        for i in r:
            if first:
                first = False
                continue

            pos = i[1].split(" ")
            x = Decimal(pos[1].lstrip("("))
            y = Decimal(pos[2].rstrip(")"))

            # points.append((x, y))
            points.append([i[0], (0.0, 0.0)])
    return points


def get_max_image(max_pixels) -> Image:
    size = 30

    im = Image.open("<BW Image>.png")
    im = im.convert("P")
    im = im.resize((size, size * 2))

    while True:
        size -= 1

        im_copy = im.resize((size, size * 2))
        black = 0

        for pix in im_copy.getdata():
            if pix:
                black += 1

        if black <= max_pixels:
            break

    print(size, black)
    return im_copy


def to_mssql(points):
    for point in points:
        print(f"UPDATE [<DB_NAME>].[dbo].[<TABLE_NAME] "
              f"SET Shape=geometry::STPointFromText('POINT({point[1][0]} {point[1][1]})', 4326) "
              f"WHERE OBJECTID = '{point[0]}';")


def main():
    points = get_points()
    points_ptr = 0
    point_count = len(points)
    im = get_max_image(point_count)
    # points = []

    for x in range(im.size[0]):
        for y in range(im.size[1]):
            if im.getpixel((x, y)):
                adj_x = (Decimal(x / im.size[0]) * deltas[0]) + limits["x"][0]
                adj_y = (Decimal((im.size[1] - y) / im.size[1]) * deltas[1]) + limits["y"][0]
                points[points_ptr][1] = (adj_x, adj_y)
                points_ptr += 1
    # im.show()
    for point in points[points_ptr:]:
        point[1] = points[0][1]

    to_mssql(points)
    # pprint(points)
    # plt.scatter(*zip(*points), s=dot_size)
    # plt.subplots_adjust(0, 0, float(deltas[0] / deltas[1]), 1)
    # plt.show()


if __name__ == "__main__":
    main()
