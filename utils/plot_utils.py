# functions to plot cool stuff
import matplotlib
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np

def see_object(obj_number, df, segmented_image,original_image,crop_value):
    #find the coordinates of the object
    coords = df.ix[obj_number][['Location_Center_X', 'Location_Center_Y']]
    x_coord = int(np.asmatrix(coords[[0]].astype(int)))
    y_coord = int(np.asmatrix(coords[[1]].astype(int)))
    #find the cropping points
    cpx1 = max(0, x_coord - crop_value)
    cpy1 = max(0, y_coord - crop_value)
    cpx2 = min(segmented_image.size[0], x_coord + crop_value)
    cpy2 = min(segmented_image.size[1], y_coord + crop_value)
    #crop images
    seg_im = segmented_image.crop((cpx1, cpy1, cpx2, cpy2))
    ori_im = original_image.crop((cpx1, cpy1, cpx2, cpy2))
    #produce the figure
    new_im = Image.new('RGB', (crop_value*4, crop_value*2))
    new_im.paste(ori_im, (0, 0))
    new_im.paste(seg_im, (crop_value*2, 0))

    return new_im


