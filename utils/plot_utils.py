# functions to plot cool stuff
# import matplotlib
# import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import pandas as pd
from matplotlib import cm
import matplotlib.pyplot as plt
import os
import random
from utils import generic_functions as gf


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


def plotPH3Cell(seriesData, datapath, window=30, lut='plasma'):
    # makes a composite plot to show the data and the processed data
    assert isinstance(seriesData, pd.Series), 'Data not pandas series'

    # find path name of image:
    C2name = os.path.join(datapath, 'ROIs--Gce_processed',
                          gf.make_image_name_from_series(seriesData, channel=2))
    C3name = os.path.join(datapath, 'ROIs--Gce_processed',
                          gf.make_image_name_from_series(seriesData, channel=3))
    C4name = os.path.join(datapath, 'ROIs--Gce_processed',
                          gf.make_image_name_from_series(seriesData, channel=4))

    # open
    c2_image = Image.open(C2name).convert('L')
    c3_image = Image.open(C3name).convert('L')
    c4_image = Image.open(C4name).convert('L')
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
    Base_name = gf.make_image_name_from_series(seriesData, channel=1).split('.tif')[0]
    PI_name = os.path.join(datapath,
                           'Cell_profiler_output',
                           Base_name + '_Result_Overlay.tiff')
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


def plotPH3Channel(seriesData, datapath, channel=1, window=30, lut='plasma'):
    # plots a single channel
    assert isinstance(seriesData, pd.Series), 'Data not pandas series'

    # find path name of image eg:
    imdir = os.path.join(datapath,
                         'ROIs--Gce_processed',
                         gf.make_image_name_from_series(seriesData, channel=channel))
    # open
    c_image = Image.open(imdir).convert('L')

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


def plot_channel_of_indexes(fig, axs, indexes, df, channel, window, lut):
    ncells = axs.shape[1]
    for row_number, set_of_idx in enumerate(indexes):
        for col_number in range(ncells):
            ax = axs[row_number, col_number]
            ax.grid(False)
            ax.axis('off')
            # evaluate if there is something to be plotted
            if col_number < len(set_of_idx):
                i = set_of_idx[col_number]
                # plt.title(str(thresholds[counter]) + " - " + str(i))
                datapath = os.path.join(df.attrs['datapath'], df.loc[i].AnimalID)
                CellImage = plotPH3Channel(df.loc[i], datapath,
                                           channel=channel, window=window, lut=lut)
                ax.imshow(CellImage)
    fig.tight_layout()

    return(fig)


def draw_ellipse(image, bounds, width=1, outline='white', antialias=4):
    """Improved ellipse drawing function, based on PIL.ImageDraw."""
    # from https://stackoverflow.com/questions/32504246/draw-ellipse-in-python-pil-with-line-thickness

    # Use a single channel image (mode='L') as mask.
    # The size of the mask can be increased relative to the imput image
    # to get smoother looking results
    mask = Image.new(
        size=[int(dim * antialias) for dim in image.size],
        mode='L', color='black')
    draw = ImageDraw.Draw(mask)

    # draw outer shape in white (color) and inner shape in black (transparent)
    for offset, fill in (width / -2.0, 'white'), (width / 2.0, 'black'):
        left, top = [(value + offset) * antialias for value in bounds[:2]]
        right, bottom = [(value - offset) * antialias for value in bounds[2:]]
        draw.ellipse([left, top, right, bottom], fill=fill)

    # downsample the mask using PIL.Image.LANCZOS
    # (a high-quality downsampling filter).
    mask = mask.resize(image.size, Image.LANCZOS)
    # paste outline color to input image through the mask
    image.paste(outline, mask=mask)


def inspect_cells_in_ROI(df, indexes_to_plot, g_name, channels, cir_radius, binning=1,
                         tdtomato_thr=-1, plot_cellprofiler=True):
    '''
    circles the cells in the dataset in the selected channels. It also shows the summary
    image of the cell profiler

    param df: dataframe. Needs data path as attributes
    param indexes_to_plot: set of indexes to plot from
    param g_name: specific ROI name in style 'PH301-1-3-R-Tail-12'
    param channels: channels to show in form of list
    param cir_radius: radius for the circles
    param binning: how much to bin the images
    param tdtomato_thr: to differentiate between d1 and d2
    param plot_cellprofiler: boolean to show the cell profiler output
    '''
    # subselect the dataframe
    df_cir = df[df.group_name == g_name]
    # get the indexes that need circling
    idxs_to_circle = np.intersect1d(indexes_to_plot, df_cir.index.values)

    # get coordinates and colors of circles to draw
    cir_coord_list = []
    cir_color_list = []
    # rescale radius
    cir_radius = int(cir_radius / binning)
    for index_of_cell in idxs_to_circle:
        # find coordinates of cells
        c_x = int(df.loc[index_of_cell].Center_X / binning)
        c_y = int(df.loc[index_of_cell].Center_Y / binning)
        # define coordinates of circle
        cir_coord = (c_x - cir_radius, c_y - cir_radius, c_x + cir_radius, c_y + cir_radius)
        cir_coord_list.append(cir_coord)

        cir_color_list.append('red')
        # TODO: make a legend for this and change the way it is implemented.
        '''
        # assign different color
        if df.loc[index_of_cell].MeanI_C3 > tdtomato_thr:
            cir_color_list.append('red')
        else:
            cir_color_list.append('green')
        '''
    # list to store the images
    im_list = []

    # get the processed data if asked to
    if plot_cellprofiler:
        concat_im = get_cp_image(df_cir)
        # resize
        new_size = tuple([int(x / binning) for x in concat_im.size])
        concat_im = concat_im.resize(new_size, Image.ANTIALIAS)
        # draw circles
        for col, cir_coord in enumerate(cir_coord_list):
            draw_ellipse(concat_im, cir_coord, outline=cir_color_list[col], width=cir_radius / 4)

    datapath = gf.get_animal_datapath(df)
    # for each channel
    for channel in channels:
        imdir = os.path.join(datapath,
                             'ROIs--Gce_processed',
                             gf.make_image_name_from_series(df_cir.iloc[0], channel=channel))
        im = Image.open(imdir)
        im = im.convert('RGB')
        # resize
        new_size = tuple([int(x / binning) for x in im.size])
        im = im.resize(new_size, Image.ANTIALIAS)
        im_list.append(im)
        # draw circles
        for col, cir_coord in enumerate(cir_coord_list):
            draw_ellipse(im, cir_coord, outline=cir_color_list[col], width=cir_radius / 4)

    # concatenate images
    if plot_cellprofiler:
        for im in im_list:
            concat_im = get_concat_h(concat_im, im)
    else:
        concat_im = im_list[0]
        for im in im_list[1:]:
            concat_im = get_concat_h(concat_im, im)

    return concat_im


def show_object_ids(df, g_name, fontsize):
    '''
    shows the summary image of the cell profiler with ids of the cells

    param df: dataframe. Needs data path as attributes
    param g_name: specific ROI name in style 'PH301-1-3-R-Tail-12'
    param fontsize: size of font
    '''
    # subselect the dataframe
    df_cir = df[df.group_name == g_name]

    # get the processed data
    proc_im = get_cp_image(df_cir)

    fnt = ImageFont.truetype("/mnt/c/Windows/Fonts/Arial.ttf", fontsize)
    d = ImageDraw.Draw(proc_im)
    for idx in df_cir.index.values:
        d.text((df_cir.loc[idx].Center_X, df_cir.loc[idx].Center_Y), str(idx),
               font=fnt, fill=(255, 0, 0))

    return(proc_im)


def get_cp_image(df):
    '''
    opens the cell profiler output image of the first object in a dataframe
    param df: dataframe. Needs data path as attributes
    '''
    Base_name = gf.make_image_name_from_series(df.iloc[0], channel=1).split('.tif')[0]
    datapath = gf.get_animal_datapath(df)
    PI_name = os.path.join(datapath,
                           'Cell_profiler_output',
                           Base_name + '_Result_Overlay.tiff')
    concat_im = Image.open(PI_name)

    return concat_im


def get_reg_image(df):
    '''
    opens the image for registration of the first object in a dataframe
    param df: dataframe. Needs data path as attributes
    '''
    reg_path = '/ROIs/000_Slices_for_ARA_registration/'
    Base_name = gf.make_image_name_from_series(df.iloc[0], channel=1).split('_manualROI')[0]
    datapath = gf.get_animal_datapath(df)
    PI_name = datapath + reg_path + Base_name + '.tif'
    reg_im = Image.open(PI_name)

    return reg_im


def get_concat_image_from_rois(df_raw, indexes_to_plot, sel_mroi_name, channel,
                               cir_radius, binning=1, tdtomato_thr=-1):
    '''
    reconstructs the image from square rois and their initial positions
    param df_raw: dataframe with information about the cells
    param indexes_to_plot: set of indexes to plot from
    param sel_mroi_name: specific ROI name in style 'PH301-1-3-R-Tail'
    param channel: channel to plot
    param binning: binarization value
    '''
    # subselect dataframe
    df = df_raw[df_raw.manual_roi_name == sel_mroi_name]

    # get the position of every ROI in a dataframe
    manual_roi_path = gf.get_manual_rois_file_path(df)
    rois_df = gf.create_dataframe_from_roi_file(manual_roi_path)

    # find the width and height (CURRENTLY THEY HAVE TO BE THE SAME (L)) of the rois
    # if there is only one roi get it from the image

    # otherwise calculate them based on positions
    L = gf.get_roi_size(rois_df.high_res_x_pos)
    if L == 0:  # all rois lie in a column
        L = gf.get_roi_size(rois_df.high_res_y_pos)
    # get the top left corner to anchor the images, and the bottom right
    xmin, xmax, ymin, ymax = gf.get_roi_position_extremes(rois_df)
    # create the big image
    im_width = int((xmax + L - xmin) / binning)
    im_height = int((ymax + L - ymin) / binning)
    im = Image.new('RGB', (im_width, im_height))
    # text object
    d = ImageDraw.Draw(im)
    fnt = ImageFont.truetype("/mnt/c/Windows/Fonts/Arial.ttf", int(400 / binning))
    # paste all images in their position
    for _, row in rois_df.iterrows():
        # get the group_name for that roi
        g_name = '-'.join([sel_mroi_name, row.roiID])
        # get image and paste circles
        sub_im = inspect_cells_in_ROI(df, indexes_to_plot, g_name, [channel],
                                      cir_radius=cir_radius, binning=binning,
                                      tdtomato_thr=tdtomato_thr, plot_cellprofiler=False)
        # get coordinates
        x_coord = int((int(row.high_res_x_pos) - xmin) / binning)
        y_coord = int((int(row.high_res_y_pos) - ymin) / binning)
        # paste in the big image
        im.paste(sub_im, (x_coord, y_coord))
        # write the number of the ROI
        d.text((x_coord, y_coord), row.roiID,
               font=fnt, fill=(0, 0, 255))

    return (im)
