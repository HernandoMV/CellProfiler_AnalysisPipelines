# functions to plot cool stuff
# import matplotlib
# import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import pandas as pd
from matplotlib import cm
import matplotlib.pyplot as plt
import os
import random


def see_object(obj_number, df, segmented_image, original_image, crop_value):
    # find the coordinates of the object
    coords = df.ix[obj_number][['Location_Center_X', 'Location_Center_Y']]
    x_coord = int(np.asmatrix(coords[[0]].astype(int)))
    y_coord = int(np.asmatrix(coords[[1]].astype(int)))
    # find the cropping points
    cpx1 = max(0, x_coord - crop_value)
    cpy1 = max(0, y_coord - crop_value)
    cpx2 = min(segmented_image.size[0], x_coord + crop_value)
    cpy2 = min(segmented_image.size[1], y_coord + crop_value)
    # crop images
    seg_im = segmented_image.crop((cpx1, cpy1, cpx2, cpy2))
    ori_im = original_image.crop((cpx1, cpy1, cpx2, cpy2))
    # produce the figure
    new_im = Image.new('RGB', (crop_value * 4, crop_value * 2))
    new_im.paste(ori_im, (0, 0))
    new_im.paste(seg_im, (crop_value * 2, 0))

    return new_im


def plotRabiesCell(seriesData, mainPath, window=30, lut='plasma'):
    # makes a composite plot to show the data and the processed data
    assert isinstance(seriesData, pd.Series), 'Data not pandas series'

    # find path name of image eg: 907817_D1_Punish_Slice1_Ipsi_rabies.tif
    Base_name = seriesData[[
        'AnimalID',
        'StarterCells',
        'cFosCondition',
        'SliceNumber',
        'BrainSide']].str.cat(sep='_')
    RI_name = Base_name + '_rabies.tif'
    CI_name = Base_name + '_cfos.tif'
    # open
    RI_Image = Image.open(mainPath + 'PulledCroppedImages/' + RI_name).convert('L')
    CI_Image = Image.open(mainPath + 'PulledCroppedImages/' + CI_name).convert('L')
    # crop
    coord_x = int(seriesData['Center_X'])
    coord_y = int(seriesData['Center_Y'])
    RI_Image = cropImage(RI_Image, [coord_x, coord_y], window)
    CI_Image = cropImage(CI_Image, [coord_x, coord_y], window)
    # recolor
    RI_Image = ChangeLUT(RI_Image, lut)
    CI_Image = ChangeLUT(CI_Image, lut)

    # get the processed data
    PI_names = [mainPath + 'CellProfilerOutput/' + Base_name + '_rabies_outlines.tiff',
                mainPath + 'CellProfilerOutput/' + Base_name + '_cFos_outlines_low.tiff',
                mainPath + 'CellProfilerOutput/' + Base_name + '_cFos_outlines_med.tiff',
                mainPath + 'CellProfilerOutput/' + Base_name + '_cFos_outlines_high.tiff']
    ProcessedImage = getProcessedImage(PI_names)
    # crop
    ProcessedImage = cropImage(ProcessedImage, [coord_x, coord_y], window)

    # produce the figure
    new_im = Image.new('RGB', (window * 6, window * 2))
    new_im.paste(RI_Image, (0, 0))
    new_im.paste(CI_Image, (window * 2, 0))
    new_im.paste(ProcessedImage, (window * 4, 0))

    # resize
    new_im = new_im.resize((300, 100), Image.ANTIALIAS)

    # return
    return new_im


def plotPH3Cell(seriesData, mainPath, window=30, lut='plasma'):
    # makes a composite plot to show the data and the processed data
    assert isinstance(seriesData, pd.Series), 'Data not pandas series'

    # find path name of image eg:
    # A2A01_95_Slide-1_slice-6_manualROI-R-Tail_squareROI-1_channel-1.tif
    Base_name = seriesData[['AnimalID', 'ExperimentalCondition']].str.cat(sep='_') + \
        '_Slide-' + seriesData.Slide + \
        '_slice-' + seriesData.Slice + '_manualROI-' + seriesData.Side + '-' + seriesData.AP + \
        '_squareROI-' + seriesData.ROI + '_'

    C2name = Base_name + 'channel-2.tif'
    C3name = Base_name + 'channel-3.tif'
    C4name = Base_name + 'channel-4.tif'

    part2 = '/'.join(seriesData.PathName_Channel1.split('\\'))[2:]
    images_path = '/mnt/c' + part2 + '/'
    # open
    c2_image = Image.open(images_path + C2name).convert('L')
    c3_image = Image.open(images_path + C3name).convert('L')
    c4_image = Image.open(images_path + C4name).convert('L')
    # crop
    coord_x = int(seriesData['Center_X'])
    coord_y = int(seriesData['Center_Y'])
    c2_image = cropImage(c2_image, [coord_x, coord_y], window)
    c3_image = cropImage(c3_image, [coord_x, coord_y], window)
    c4_image = cropImage(c4_image, [coord_x, coord_y], window)
    # recolor
    c2_image = ChangeLUT(c2_image, lut)
    c3_image = ChangeLUT(c3_image, lut)
    c4_image = ChangeLUT(c4_image, lut)

    # get the processed data
    PI_name = mainPath + Base_name + 'channel-1_Result_Overlay.tiff'
    ProcessedImage = Image.open(PI_name)
    # crop
    ProcessedImage = cropImage(ProcessedImage, [coord_x, coord_y], window)

    # produce the figure
    new_im = Image.new('RGB', (window * 8, window * 2))
    new_im.paste(ProcessedImage, (0, 0))
    new_im.paste(c2_image, (window * 2, 0))
    new_im.paste(c3_image, (window * 4, 0))
    new_im.paste(c4_image, (window * 6, 0))

    # resize
    new_im = new_im.resize((400, 100), Image.ANTIALIAS)

    # return
    return new_im


def plotPH3Channel(seriesData, channel=1, window=30, lut='plasma'):
    # plots a single channel
    assert isinstance(seriesData, pd.Series), 'Data not pandas series'

    # find path name of image eg:
    # A2A01_95_Slide-1_slice-6_manualROI-R-Tail_squareROI-1_channel-1.tif
    Base_name = seriesData[['AnimalID', 'ExperimentalCondition']].str.cat(sep='_') + \
        '_Slide-' + seriesData.Slide + \
        '_slice-' + seriesData.Slice + '_manualROI-' + seriesData.Side + '-' + seriesData.AP + \
        '_squareROI-' + seriesData.ROI + '_'

    Cname = Base_name + 'channel-' + str(channel) + '.tif'

    part2 = '/'.join(seriesData.PathName_Channel1.split('\\'))[2:]
    images_path = '/mnt/c' + part2 + '/'
    # open
    c_image = Image.open(images_path + Cname).convert('L')

    # crop
    coord_x = int(seriesData['Center_X'])
    coord_y = int(seriesData['Center_Y'])
    c_image = cropImage(c_image, [coord_x, coord_y], window)

    # recolor
    c_image = ChangeLUT(c_image, lut)

    # resize
    c_image = c_image.resize((100, 100), Image.ANTIALIAS)

    # return
    return c_image


def cropImage(im, coords, crop_value):
    # find the coordinates of the object
    x_coord = int(coords[0])
    y_coord = int(coords[1])
    # find the cropping points
    cpx1 = max(0, x_coord - crop_value)
    cpy1 = max(0, y_coord - crop_value)
    cpx2 = min(im.size[0], x_coord + crop_value)
    cpy2 = min(im.size[1], y_coord + crop_value)
    # crop images
    croppedIm = im.crop((cpx1, cpy1, cpx2, cpy2))
    return croppedIm


def ChangeLUT(im, lut):
    lut = cm.get_cmap(lut)
    im = np.array(im)
    im = lut(im)
    im = np.uint8(im * 255)
    im = Image.fromarray(im)
    return im


def getProcessedImage(pathsToImages):
    # reads a list of 4 images (white, r, g, b), and overlaps them
    w = np.asarray(Image.open(pathsToImages[0]).convert('L'), dtype='uint8')
    r = np.asarray(Image.open(pathsToImages[1]).convert('L'), dtype='uint8')
    g = np.asarray(Image.open(pathsToImages[2]).convert('L'), dtype='uint8')
    b = np.asarray(Image.open(pathsToImages[3]).convert('L'), dtype='uint8')
    # Merge channels
    im1 = np.stack((w, w, w), axis=2).astype('uint8')
    im2 = np.stack((r, g, b), axis=2).astype('uint8')
    # add them
    out_im = Image.fromarray(im1 + im2)

    return out_im


def plot_pie(data_frame, column_names=None, cutoff=0, ax=None, **plot_kwargs):
    # Plots a pie chart of combination of channels

    if ax is None:
        ax = plt.gca()

    BinMat = data_frame[column_names] > cutoff

    # Measure combinations
    lab1 = column_names[0] + ' +'
    lab2 = column_names[1] + ' +'
    lab3 = lab1 + '\n' + lab2
    labels = lab1, lab2, lab3

    # Cells possitive for channel 1
    C1Pos = BinMat[BinMat[column_names[0]]] == True
    d1PosCellsID = set(C1Pos.index)
    # Cells possitive for channel 2
    C2Pos = BinMat[BinMat[column_names[1]]] == True
    d2PosCellsID = set(C2Pos.index)

    comb1 = (d1PosCellsID - d2PosCellsID)
    comb2 = (d2PosCellsID - d1PosCellsID)
    comb3 = (d2PosCellsID & d1PosCellsID)

    # Create a Pie Chart
    # Data to plot
    sizes = [len(comb1), len(comb2), len(comb3)]
    colors = ['yellowgreen', 'lightcoral', 'lightskyblue']
    explode = (0, 0, 0)  # explode 1st slice

    # Plot
    ax.pie(
        sizes, explode=explode, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True, startangle=140)

    ax.axis('equal')

    return ax


def make_core_name(mouse, expcon, region, manroi):
    mrpieces = manroi.split('-')
    name = '_'.join([mouse,
                     expcon,
                     'slide-' + mrpieces[0],
                     'slice-' + mrpieces[1],
                     'manualROI-' + mrpieces[2] + '-' + region])
    return name


def summary_image_name_maker(directory, corename):
    imname = '_'.join([corename,
                       'summaryImage.tif'])
    return os.path.join(directory, imname)


def create_merge_ROI(roi_paths):
    # open images
    dapi_image = Image.open(roi_paths[0])
    c1_image = Image.open(roi_paths[1])
    c2_image = Image.open(roi_paths[2])
    # create a merge of three images
    roi_image = Image.merge('RGB', [c2_image, c1_image, dapi_image])

    return roi_image


def get_channel_name(corename, roi, channel):
    roiname = '-'.join(['squareROI', str(roi)])
    channame = '-'.join(['channel', str(channel)])

    return '_'.join([corename, roiname, channame])


def get_roi_path(directory, corename, roi, channel):
    # builds the path to the channel image
    im_name = get_channel_name(corename, roi, channel) + '.tif'

    return os.path.join(directory, im_name)


def get_cp_path(directory, imname):
    modname = imname + '_Result_Overlay.tiff'

    return os.path.join(directory, modname)


def get_concat_h(im1, im2):
    dst = Image.new('RGB', (im1.width + im2.width, im1.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst


def get_random_rois(df, mouse, manroi, k):
    roipieces = manroi.split('-')
    slide = roipieces[0]
    mysl = roipieces[1]
    side = roipieces[2]

    conds = np.logical_and(df.AnimalID == mouse, df.Slide == slide)
    conds = np.logical_and(df.Slice == mysl, conds)
    conds = np.logical_and(df.Side == side, conds)
    unique_rois = df[conds].ROI.unique()

    return random.sample(list(unique_rois), k)
