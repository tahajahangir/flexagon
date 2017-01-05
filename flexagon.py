#!/usr/bin/env python
###############################################################################
# Simple PIL-based flexagon generator
#
# For the time being, it creates only 3D trihexaflexagons.
#
# Daniel Prokesch <daniel.prokesch@gmail.com>
###############################################################################
"""USAGE: {} image1 image2 image3 image4 output"""
import math
from PIL import Image, ImageOps, ImageDraw
from math import sqrt, sin, cos, pi

import sys

# The flexagon is composed of small equilateral triangles.
min_angle = pi / 3  # tiangle's smallest angle: 60 degree
# min_angle = math.atan(0.5) * 2
# The height equals width * sqrt(3)/2
height_to_width = 1 / (2 * math.tan(min_angle / 2))


def crop_size(img):
    """Crop the image to have the appropriate ratio for a flexagon."""
    width, height = img.size
    # could use fit, with the assumption that the height will be sufficient
    #   return ImageOps.fit(img, (width, int(width * sqrt3_2)))
    # better make a case distinction
    if height > (width * height_to_width):
        new_height = int(width * height_to_width)
        diff_2 = (height - new_height) / 2
        # left, upper, right, lower
        box = (0, diff_2, width, diff_2 + new_height)
    else:
        new_width = int(height / height_to_width)
        diff_2 = (width - new_width) / 2
        # left, upper, right, lower
        box = (diff_2, 0, diff_2 + new_width, height)
    return img.crop(box)


def rot_trans(center, angle, new_center):
    """Return an array for PIL's affine transform.

    It describes a rotation of angle degrees around center, followed by a
    translation to new_center.

    According to PIL's documentation,
    'For each pixel (x, y) in the output image, the new value is taken from a
    position (a x + b y + c, d x + e y + f) in the input image, rounded to
    nearest pixel.'
    As result, the matrix is not an object transform matrix but an axis
    transform matrix (inverse of the former).
    """
    rho = angle * pi / 180.0
    cosine, sine = cos(rho), sin(rho)
    cx, cy = center
    nx, ny = new_center
    return [cosine, sine, -nx * cosine - ny * sine + cx,
            -sine, cosine, nx * sine - ny * cosine + cy]


def xform(mat, pt):
    """Apply the transformation of mat to a point pt.

    The transform in mat is described by a 6-element tuple, as returned by
    rot_trans.
    """
    x, y = pt
    return (x * mat[0] + y * mat[1] + mat[2],
            x * mat[3] + y * mat[4] + mat[5])


def xform_arr(mat, arr):
    """Apply the transformation of mat to a sequence arr of points."""
    return [xform(mat, pt) for pt in arr]


###############################################################################

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print >> sys.stderr, __doc__.format(sys.argv[0])
        exit(1)

    try:
        images = [crop_size(Image.open(sys.argv[i])) for i in range(1, 5)]
    except IOError as e:
        print >> sys.stderr, e
        exit(1)
    common_size = min(img.size for img in images)
    for img in images:
        img.thumbnail(common_size)

    triangle_width, triangle_height = map(lambda x: x / 2, common_size)
    flexagon = Image.new("RGB", map(int, (2.5 * triangle_width, 7 * triangle_height)), color=(255, 255, 255))


    def paste_and_mask(img, angle_degree, new_center, poly_base):
        """Get a patch from img and paste it to the flexagon."""
        mat = rot_trans(center=(triangle_width, triangle_height), angle=angle_degree, new_center=new_center)
        patch = img.transform(flexagon.size, Image.AFFINE, mat)
        mask = Image.new("1", flexagon.size)
        # The mask polygon is only translated. As rot_trans describes an axis
        # transformation, we specify the translation as center.
        mask_trans = rot_trans(new_center, 0, (0, 0))
        ImageDraw.Draw(mask).polygon(xform_arr(mask_trans, poly_base), fill=1)
        flexagon.paste(patch, (0, 0), mask)


    mask_lozi = [(0, 0), (-triangle_width / 2, triangle_height), (-triangle_width, 0),
                 (-triangle_width / 2, -triangle_height)]

    paste_and_mask(images[0], 000, (1.0 * triangle_width, 2 * triangle_height), mask_lozi)
    paste_and_mask(images[0], 120, (1.0 * triangle_width, 4 * triangle_height), mask_lozi)
    paste_and_mask(images[0], 240, (1.0 * triangle_width, 6 * triangle_height), mask_lozi)
    paste_and_mask(images[1], 000, (1.5 * triangle_width, 1 * triangle_height), mask_lozi)
    paste_and_mask(images[1], 120, (1.5 * triangle_width, 3 * triangle_height), mask_lozi)
    paste_and_mask(images[1], 240, (1.5 * triangle_width, 5 * triangle_height), mask_lozi)
    paste_and_mask(images[2], 000, (2.0 * triangle_width, 2 * triangle_height), mask_lozi)
    paste_and_mask(images[2], 120, (2.0 * triangle_width, 4 * triangle_height), mask_lozi)
    paste_and_mask(images[2], 240, (2.0 * triangle_width, 6 * triangle_height), mask_lozi)
    paste_and_mask(images[3], 000, (2.5 * triangle_width, 1 * triangle_height), mask_lozi)
    paste_and_mask(images[3], 120, (2.5 * triangle_width, 3 * triangle_height), mask_lozi)
    paste_and_mask(images[3], 240, (2.5 * triangle_width, 5 * triangle_height), mask_lozi)
    # # each patch has three parameters:
    # # rotation in degrees, the translation w.r.t. the centre point, and the
    # # mask (which is designed as to be translated with the same coordinates)
    # t1_AB = 90, (triangle_height, 1.5 * triangle_width), mask_poly_left
    # t1_CF = -30, (0, 3.0 * triangle_width), mask_poly_left
    # t1_DE = -150, (triangle_height, 4.5 * triangle_width), mask_poly_left
    #
    # t2_AB = 90, (0, 2.0 * triangle_width), mask_poly_left
    # t2_CF = -30, (triangle_height, 3.5 * triangle_width), mask_poly_left
    # t2_D = -150, (triangle_height, 0.5 * triangle_width), mask_poly_right_down
    # t2_E = -150, (0, 5.0 * triangle_width), mask_poly_right_up
    #
    # t3_A = 150, (0, 1.0 * triangle_width), mask_poly_right_down
    # t3_BC = 30, (triangle_height, 2.5 * triangle_width), mask_poly_left
    # t3_EF = -90, (0, 4.0 * triangle_width), mask_poly_left
    # t3_D = 150, (triangle_height, 5.5 * triangle_width), mask_poly_right_up
    #
    # for t in [t1_AB, t1_CF, t1_DE]:
    #     paste_and_mask(images[0], *t)
    #
    # for t in [t2_AB, t2_CF, t2_D, t2_E]:
    #     paste_and_mask(images[1], *t)
    #
    # for t in [t3_A, t3_BC, t3_EF, t3_D]:
    #     paste_and_mask(images[2], *t)

    flexagon.save(sys.argv[5])
