
Simple 2D Trihexaflexagon generator
===================================

About
-----

[Flexagons][1] are fascinating.
I came across the [great flexagon page by Dale Wiles][2], which provides
nice templates for 2D and 3D flexagons suitable for 3 and 4 images,
respecitvely.  It also contains a tool for creating your own flexagons.

I wanted to have a simpler image handling, and something that is less
resource demanding. So I gave it a shot and wrote my own script to create
simple trihexaflexagons from images.



Getting started
---------------

    ./flexagon.py image1.jpg image2.jpg image3.jpg output.jpg


The script takes the center area of each input image (aspect ratio is kept)
and downscales the larger two of the three images.


The layout and captions of the patches follow the
[image on the flexagon page][3].

You can follow the instructions on the [page][2] for folding your flexagon.



Requirements
------------

Requires Pillow (tested with Pillow 2.3.0, 3.0.0 and 3.4.1):

    pip install Pillow



Contribute
----------

If you want to contribute, you can extend the script to support more types
of flexagons.

This project is published under the [MIT License](./LICENSE).


[1]: https://en.wikipedia.org/wiki/Flexagon
[2]: http://modarnis.com/flexagon/
[3]: http://modarnis.com/flexagon/flex_2d/example_large_01.png
