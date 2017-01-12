#!/usr/bin/env python
###############################################################################
# Simple PIL-based flexagon generator
#
# For the time being, it creates only 3D trihexaflexagons.
#
# Daniel Prokesch <daniel.prokesch@gmail.com>
###############################################################################
"""USAGE: {} image1 image2 image3 image4 output"""
from __future__ import print_function

import sys
from math import sin, cos, pi, sqrt

from PIL import Image, ImageDraw


def crop_size(img, height_to_width):
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


def rot_scale_trans(center, scale_x_ratio, angle, new_center):
    """Return an array for PIL's affine transform.

    It describes a rotation of angle degrees around center, followed by a
    scale, followed by a translation to new_center.

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
    sw = scale_x_ratio
    # This matrix is computed as this: https://goo.gl/fcgF56
    return [cosine / sw, sine, cx - nx * cosine / sw - ny * sine,
            -sine / sw, cosine, cy + nx * sine / sw - ny * cosine]


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

def main(input_files, output_file):
    # The flexagon is composed of small equilateral triangles.
    height_to_width = 2.0 / sqrt(3)

    images = [crop_size(Image.open(fn), height_to_width) for fn in input_files]
    common_size = min(img.size for img in images)
    scale_all = 0.3
    if scale_all != 1:
        common_size = (common_size[0] * scale_all, common_size[1] * scale_all)
    img_center = (common_size[0] / 2, common_size[1] / 2)
    for img in images:
        img.thumbnail(common_size)

    in_triangle_height, in_triangle_width = map(lambda x: x / 2, common_size)
    out_triangle_width = in_triangle_width
    scale_height_ratio = 2 / sqrt(3)
    out_triangle_height = in_triangle_height * scale_height_ratio
    # add additional 1-pixel for line drawing
    flexagon = Image.new("RGB", (int(7 * out_triangle_height), int(2.5 * out_triangle_width) + 1), color=(255, 255, 255))

    def paste_and_mask(img, angle_degree, new_center, poly_base):
        """Get a patch from img and paste it to the flexagon."""
        mat = rot_scale_trans(center=img_center, angle=angle_degree, new_center=new_center,
                              scale_x_ratio=scale_height_ratio)
        patch = img.transform(flexagon.size, Image.AFFINE, mat)
        mask = Image.new("1", flexagon.size)
        # The mask polygon is only translated. As rot_trans describes an axis
        # transformation, we specify the translation as center.
        mask_trans = rot_scale_trans(new_center, 1, 0, (0, 0))
        poly_box = xform_arr(mask_trans, poly_base)
        ImageDraw.Draw(mask).polygon(poly_box, fill=1)
        flexagon.paste(patch, (0, 0), mask)
        ImageDraw.Draw(flexagon).polygon(poly_box, outline=(0, 0, 0))

    diamond_mask = [(0, 0), (-out_triangle_width / 2, out_triangle_height), (-out_triangle_width, 0),
                    (-out_triangle_width / 2, -out_triangle_height)]
    diamond_mask = [(0, -out_triangle_width), (out_triangle_height, -out_triangle_width / 2),
                    (0, 0), (-out_triangle_height, -out_triangle_width / 2)]

    def draw_img(img, alpha_offset, offset_width, offset_height):
        paste_and_mask(img, alpha_offset + 120,
                       (offset_height * out_triangle_height, offset_width * out_triangle_width),
                       diamond_mask)
        paste_and_mask(img, alpha_offset, ((offset_height + 2) * out_triangle_height,
                                           offset_width * out_triangle_width), diamond_mask)
        paste_and_mask(img, alpha_offset - 120, ((offset_height + 4) * out_triangle_height,
                                                 offset_width * out_triangle_width), diamond_mask)

    draw_img(images[0], 0, 1.0, 2)
    draw_img(images[1], 60, 1.5, 1)
    draw_img(images[2], 0, 2.0, 2)
    draw_img(images[3], 60, 2.5, 1)

    ImageDraw.Draw(flexagon).line([
        (out_triangle_height, out_triangle_width / 2),
        (0, 0),
        (0, out_triangle_width * 2.5),
        (2 * out_triangle_height, out_triangle_width * 2.5),
        (2 * out_triangle_height, out_triangle_width * 2),
        (2 * out_triangle_height, out_triangle_width * 2.5),
        (4 * out_triangle_height, out_triangle_width * 2.5),
        (4 * out_triangle_height, out_triangle_width * 2),
        (4 * out_triangle_height, out_triangle_width * 2.5),
        (6 * out_triangle_height, out_triangle_width * 2.5),
        (6 * out_triangle_height, out_triangle_width * 2),
    ], fill=(0, 0, 0))

    flexagon.save(output_file)


if __name__ == "__main__":
    if len(sys.argv) != 6:
        print(__doc__.format(sys.argv[0]), file=sys.stderr)
        exit(1)
    main(sys.argv[1:5], sys.argv[5])
