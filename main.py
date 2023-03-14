import sys

# install with 'pip install numpy'
import numpy

# install with 'pip install pyvips'
import pyvips

# it is bundled with...
from colormaps import RdYlGn_lut

numpy.set_printoptions(threshold=numpy.inf)


# find min/max and histogram
def result_histogram(result):
    np_2d = numpy.ndarray(
        buffer=result.get_memory(),
        dtype=numpy.float32,
        shape=[result.height, result.width]
    )

    flat_result = np_2d.flatten()

    histogram = numpy.histogram(flat_result, bins=256)[0]
    return histogram


# Remaps value (that has an expected range of in_low to in_high) into a target range of to_low to to_high
def math_map_value(value, in_low, in_high, to_low, to_high):
    return to_low + (value - in_low) * (to_high - to_low) / (in_high - in_low)


# return image bands depending of band_order
def bandsplit(image, band_order):
    if band_order == 'GRN':
        second, first, third, alpha = image.bandsplit()
    else:
        first, second, third, alpha = image.bandsplit()

    return [first, second, third, alpha]


# apply image manipulation algebra
# VARI
def calculate_vari(image, band_order):
    r, g, b, alpha = bandsplit(image, band_order)
    index = (g - r) / (g + r - b)
    return [index]


def apply_vari(input_file):
    # load image
    image = pyvips.Image.new_from_file('./' + input_file)

    # calculate VARI
    result = calculate_vari(image, 'RGB')[0]

    # get histogram
    histogram = result_histogram(result)

    # apply Look-Up-Table (LUT)
    rdylgn_image = pyvips.Image.new_from_array(RdYlGn_lut).bandfold()
    rgb = result.maplut(rdylgn_image)

    # save to file
    rgb.write_to_file('./vari_python_generated.png')


apply_vari(sys.argv[1])
