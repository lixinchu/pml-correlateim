import os

import click

# QT imports
# from PyQt5.QtWidgets import QApplication, QWidget, QLabel
# from PyQt5.QtGui import QIcon, QPixmapfrom

import matplotlib.pyplot as plt
import numpy as np
import skimage.color
import skimage.transform

from correlateim import imageproc
from correlateim import transform
import correlateim.cpselect
from correlateim.io import save_json, save_text


def _transform_images(transformation, image_filename_1, image_filename_2):
    """Align images from files and a transformation matrix.

    Parameters
    ----------
    transformation : ndarray
        Affine transform matrix, as a numpy array.
    image_filename_1 : str
        Path to image 1 (eg: the FLUORESCENCE image)
    image_filename_2 : str
        Path to image 2 (eg: the FIBSEM image)

    Returns
    -------
    ndarray
        Blended 2D RGB image.
    """
    image_1 = skimage.color.gray2rgb(plt.imread(image_filename_1))
    image_2 = skimage.color.gray2rgb(plt.imread(image_filename_2))
    image_1 = skimage.transform.resize(image_1, image_2.shape,
                                       anti_aliasing=True)
    image_1_aligned = transform.apply_transform(image_1, transformation)
    image_1_aligned = np.clip(image_1_aligned, 0.0, 1.0)
    for i in range(3):
        r = image_1_aligned[:, :, i]
        r[r == 0] = 0.92
        image_1_aligned[:, :, i] = r
    # result = imageproc.overlay_images(image_1_aligned, image_2)
    return image_1_aligned

def _align_images(transformation, image_filename_1, image_filename_2):
    """Align images from files and a transformation matrix.

    Parameters
    ----------
    transformation : ndarray
        Affine transform matrix, as a numpy array.
    image_filename_1 : str
        Path to image 1 (eg: the FLUORESCENCE image)
    image_filename_2 : str
        Path to image 2 (eg: the FIBSEM image)

    Returns
    -------
    ndarray
        Blended 2D RGB image.
    """
    image_1 = skimage.color.gray2rgb(plt.imread(image_filename_1))
    image_2 = skimage.color.gray2rgb(plt.imread(image_filename_2))
    image_1 = skimage.transform.resize(image_1, image_2.shape,
                                       anti_aliasing=True)
    image_1_aligned = transform.apply_transform(image_1, transformation)
    result = imageproc.overlay_images(image_1_aligned, image_2)
    return result


# def correlate_images(image_filename_1, image_filename_2, output_filename):
def correlate_images(image_filename_1, output_filename):

    """Correlate two image files by interactively selecting control points.

    Parameters
    ----------
    image_filename_1 : str
        Path to image 1 (eg: the FLUORESCENCE image)
    image_filename_2 : str
        Path to image 2 (eg: the FIBSEM image)
    output_filename : str
        Filename for output, must have .png file extension.

    Returns
    -------
    ndarray
        Blended 2D RGB image.

    Notes
    -----
    Will save outputs:
    (1) Image overlay; blended 2D RGB image saved as .png
    (2) Text file with control points and matrix transform, saved as .txt
    (3) The affine transformation matrix, saved as .npy (read with numpy.load())
    """
    # User select matched control points
    # matched_points_dict = correlateim.cpselect.cpselect_read_files(
    #     image_filename_1, image_filename_2)
    matched_points_dict = correlateim.cpselect.cpselect_read_files(image_filename_1)
    if matched_points_dict == []:
        print('No control points selected, exiting.')
        return
    print(matched_points_dict)

    # Calculate and apply affine transformation
    # src, dst = transform.point_coords(matched_points_dict)
    # transformation = transform.calculate_transform(src, dst)
    # result = _align_images(transformation, image_filename_1, image_filename_2)

    # Finish and tidy up
    # save_text(image_filename_1, image_filename_2, output_filename,
    #           transformation, matched_points_dict)  # saves text summary
    if output_filename is not None:
        save_json(output_filename, matched_points_dict) # saves JSON of selected landmarks
        print('Saved point coordinates to: {}'.format(output_filename))
    # plt.imsave(output_filename, result)
    # print('Saved image overlay result to: '
    #       '{}'.format(os.path.abspath(output_filename)))

    # plt.imshow(result)
    # plt.show()
    # return result
    print("Done!")
    return


def correlate_from_file(transformation_filename,
                        image_filename_1,
                        image_filename_2,
                        output_filename):
    """Correlate images from filenames using a previously saved transformation.

    Parameters
    ----------
    transformation_filename : str
        The affine transformation matrix saved as a .npy file
    image_filename_1 : str
        Path to image 1 (eg: the FLUORESCENCE image)
    image_filename_2 : str
        Path to image 2 (eg: the FIBSEM image)
    output_filename : str
        Filename for output, must have .png file extension.

    Returns
    -------
    ndarray
        Blended 2D RGB image.

    Notes
    -----
    Will save outputs:
    (1) Image overlay; blended 2D RGB image saved as .png
    """
    # Align images from an existing transformation array
    transformation = np.load(transformation_filename)
    result = _transform_images(transformation, image_filename_1, image_filename_2)
    # Finish and tidy up
    plt.imsave(output_filename, result)
    print('Saved image overlay result to: '
          '{}'.format(os.path.abspath(output_filename)))
    #plt.imshow(result)
    #plt.show()
    return result


@click.command()
@click.argument('transformation_filename')
@click.argument('image_filename_1')
@click.argument('image_filename_2')
@click.argument('output_filename')
def main_from_file(transformation_filename, image_filename_1, image_filename_2,
                   output_filename):
    """Correlate images from filenames using a previously saved transformation.

    Parameters
    ----------
    transformation_filename : str
        The affine transformation matrix saved as a .npy file
    image_filename_1 : str
        Path to image 1 (eg: the FLUORESCENCE image)
    image_filename_2 : str
        Path to image 2 (eg: the FIBSEM image)
    output_filename : str
        Filename for output, must have .png file extension.

    Returns
    -------
    ndarray
        Blended 2D RGB image.

    Notes
    -----
    Will save output:
    (1) Image overlay; blended 2D RGB image saved as .png
    """
    result = correlate_from_file(transformation_filename,
                                 image_filename_1,
                                 image_filename_2,
                                 output_filename)
    return result


@click.command()
@click.argument('image_filename_1')
# @click.argument('image_filename_2')
@click.argument('output_filename', required=False)
def main(image_filename_1, output_filename=None):
# def main(image_filename_1, image_filename_2, output_filename):
    """Correlate two images using matched control points.

    Parameters
    ----------
    image_filename_1 : str
        Path to image 1 (eg: the FLUORESCENCE image)
    image_filename_2 : str
        Path to image 2 (eg: the FIBSEM image)
    output_filename : str
        Filename for output, must have .png file extension.

    Returns
    -------
    ndarray
        Blended 2D RGB image.

    Notes
    -----
    Will save outputs:
    (1) Image overlay; blended 2D RGB image saved as .png
    (2) Text file with control points and matrix transform, saved as .txt
    (3) The affine transformation matrix, saved as .npy (read with numpy.load())
    """
    # result = correlate_images(image_filename_1,
    #                           image_filename_2,
    #                           output_filename)

    result = correlate_images(image_filename_1, output_filename)
    return result


if __name__ == '__main__':
    # main_from_file()
    main()
