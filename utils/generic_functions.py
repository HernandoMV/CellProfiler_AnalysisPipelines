import numpy as np
import pandas as pd
import os
from PIL import Image
import sys
sys.path.append("../") # go to parent 
from Fiji_Custom.functions.text_manipulation import get_registered_slices_folder


def get_indexes_by_thr(df, sc, thresholds, n):
    '''
    find random indexes belonging to certain thresholds for a column in a dataframe
    param df is a dataframe
    param sc is the name of a column in the dataframe
    param thresholds is a tuple of tuples e.g: ((0, .1), (.2, .3), ...)
    param n is the number of indexes to return for each threshold band
    returns list of lists of random indexes for each threshold category
    '''
    # initialize list to return
    indexes = []
    for tr in thresholds:
        # get the values of the indexes
        shuffledIdx = df[np.logical_and(df[sc] >= tr[0], df[sc] < tr[1])].index.values.copy()
        # shuffle them
        np.random.shuffle(shuffledIdx)
        # append, else append empty
        if len(shuffledIdx) > 0:
            indexes.append(list(shuffledIdx[0:n]))
        else:
            indexes.append([])

    return(indexes)


def make_slice_name_from_series(series_data):
    '''
    series_data is a panda series with specific columns
    outputs: PH301_A2A-Ai14_slide-1_slice-0
    '''

    assert isinstance(series_data, pd.Series), 'Data not pandas series'
    name = '_'.join([series_data.AnimalID,
                     series_data.ExperimentalCondition,
                     'slide-' + series_data.Slide,
                     'slice-' + series_data.Slice])
    return name


def make_core_name_from_series(series_data):
    '''
    series_data is a panda series with specific columns
    outputs: PH301_A2A-Ai14_slide-1_slice-0_manualROI-L-Tail
    '''

    assert isinstance(series_data, pd.Series), 'Data not pandas series'
    name = '_'.join([make_slice_name_from_series(series_data),
                     'manualROI-' + series_data.Side + '-' + series_data.AP])
    return name


def make_image_name_from_series(series_data, channel):
    '''
    series_data is a panda series with specific columns
    outputs: PH301_A2A-Ai14_slide-1_slice-0_manualROI-L-Tail_squareROI-1_channel-1
    '''

    assert isinstance(series_data, pd.Series), 'Data not pandas series'
    name = '_'.join([make_core_name_from_series(series_data),
                     'squareROI-' + series_data.ROI,
                     'channel-' + str(channel)])
    return name + '.tif'


def group_name(df):
    # Create a unique identifier for every instance of measure (individual ROI)
    return '-'.join(df[['AnimalID', 'Slide', 'Slice', 'Side', 'AP', 'ROI']])


def manual_roi_name(df):
    # Create a unique identifier for every instance of measure (manual ROI)
    return '-'.join(df[['AnimalID', 'Slide', 'Slice', 'Side', 'AP']])


def get_roi_size(series_data):
    '''returns difference between elements of a panda series'''
    assert isinstance(series_data, pd.Series), 'Data not pandas series'
    # get unique elements
    un_els = pd.to_numeric(series_data.unique())
    # if only one column or row, return 0
    if len(un_els) == 1:
        return(0)
    # get difference between unique elements
    un_els_dif = np.diff(un_els)
    # if the difference is not the same
    assert any(x == un_els_dif[0] for x in un_els_dif), 'ROIs of distinct size'

    return(un_els_dif[0])


def create_dataframe_from_roi_file(filepath):
    '''
    creates a dataframe with information of rois
    '''
    # initialize list to hold the data
    rois_list = []
    # read from the file and populate the dictionary
    linecounter = 0
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            parts = line.split(', ')
            # read column names from first line
            if linecounter == 0:
                columns = parts
            else:  # append to the list
                rois_list.append(parts)
            linecounter += 1

    # create the dataframe
    rois_df = pd.DataFrame(data=rois_list, columns=columns)

    return(rois_df)


def get_manual_rois_file_path(df):
    '''
    generates the path to the file with the rois information
    '''
    rois_file_path = 'ROIs/000_ManualROIs_info/'
    datapath = get_animal_datapath(df)
    manual_roi_path = os.path.join(datapath,
                                   rois_file_path,
                                   make_core_name_from_series(df.iloc[0]))
    manual_roi_path = '_'.join([manual_roi_path,
                               'roi_positions.txt'])

    return (manual_roi_path)


def get_roi_position_extremes(df):
    '''
    returns extreme values for the position of the rois
    '''
    min_x = np.min(pd.to_numeric(df.high_res_x_pos))
    max_x = np.max(pd.to_numeric(df.high_res_x_pos))
    min_y = np.min(pd.to_numeric(df.high_res_y_pos))
    max_y = np.max(pd.to_numeric(df.high_res_y_pos))

    return (min_x, max_x, min_y, max_y)


def get_animal_datapath(df):
    mainpath = df.attrs['datapath']
    animal_id = df.AnimalID.unique()[0]
    return os.path.join(mainpath, animal_id)


def register_cell_to_ARA(series_data, main_path):
    # assess that input is a pd.series
    assert isinstance(series_data, pd.Series), 'Data not pandas series'
    # assess if the slice is registered
    reg_field_filepath, registered_resolution = get_registration_field_file_path(series_data, main_path)
    if not os.path.isfile(reg_field_filepath):
        print('This file does not exist: {}'.format(reg_field_filepath))
        return
    # find the absolute pixel location of the cells
    x, y = get_prereg_coordinates(series_data, main_path, registered_resolution)

    im = Image.open(reg_field_filepath)
    vals = []
    for i in range(im.n_frames):
        im.seek(i)
        vals.append(im.getpixel((x, y)))
    ap = vals[0]
    dv = vals[1]
    ml = vals[2]
    return [ap, dv, ml]
    

def get_registration_field_file_path(series_data, main_path):
    # assess that input is a pd.series
    assert isinstance(series_data, pd.Series), 'Data not pandas series'
    # construct the expected file name
    slice_name = make_slice_name_from_series(series_data)
    # registration folder path
    reg_folder_path = os.path.join(main_path,
                                   series_data.AnimalID,
                                   'Registration')
    # find the folder containing the information
    reg_images_folder, registered_resolution = get_registered_slices_folder(reg_folder_path)
    
    file_path = os.path.join(reg_images_folder, slice_name + '.tif_ch0_Coords.tif')

    return file_path, registered_resolution


def get_prereg_coordinates(series_data, data_path, reg_im_res=0):
    '''
    series_data is a panda data series with specific columns
    datapath is the path to the images
    reg_im_res is the resolution, in microns, of the image used for registration
    outputs: general coordinates of cell in downsampled image
    '''
    assert isinstance(series_data, pd.Series), 'Data not pandas series'

    # get the path to the file with roi information
    mr_file = get_manual_rois_file_path(series_data, data_path)
    # generate a dataframe from that file
    roi_df = create_dataframe_from_roi_file(mr_file)

    rn = str(series_data.ROI)
    roi_df_bool = roi_df.roiID == rn
    # get high resolution x and y values
    hr_x = int(roi_df[roi_df_bool].high_res_x_pos) + float(series_data.Center_X)
    hr_y = int(roi_df[roi_df_bool].high_res_y_pos) + float(series_data.Center_Y)
    # adjust resolution
    if reg_im_res==0: # if registration resolution is not supplied, find it in the file
        reg_im_res = float(roi_df[roi_df_bool].registration_image_pixel_size)
    coords_res = float(roi_df[roi_df_bool].high_res_pixel_size)
    lr_x = int(hr_x * coords_res / reg_im_res)
    lr_y = int(hr_y * coords_res / reg_im_res)

    return lr_x, lr_y


def create_dataframe_from_roi_file(filepath):
    '''
    creates a dataframe with information of rois
    '''
    # initialize list to hold the data
    rois_list = []
    # read from the file and populate the dictionary
    linecounter = 0
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            parts = line.split(', ')
            # read column names from first line
            if linecounter == 0:
                columns = parts
            else:  # append to the list
                rois_list.append(parts)
            linecounter += 1

    # create the dataframe
    rois_df = pd.DataFrame(data=rois_list, columns=columns)

    return(rois_df)


def get_manual_rois_file_path(series_data, data_path):
    '''
    generates the path to the file with the rois information
    '''
    rois_file_path = 'ROIs/000_ManualROIs_info/'
    manual_roi_path = os.path.join(data_path,
                                   series_data.AnimalID,
                                   rois_file_path,
                                   make_core_name_from_series(series_data))
    manual_roi_path = '_'.join([manual_roi_path,
                               'roi_positions.txt'])

    return (manual_roi_path)