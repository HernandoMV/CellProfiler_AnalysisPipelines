
import pandas as pd
import os
import glob
import numpy as np


def data_reader(file, channelnumber):
    # reads data from CellProfiler output Nuclei.csv
    f = open(file)
    # read data into a dictionary where each entry is the nuclei number
    data = pd.read_csv(f)
    assert isinstance(data, object)

    # select only important fields
    data = data.apply(pd.to_numeric)
    if channelnumber == 2:
        return data[[
            'ObjectNumber',
            'Children_FinalDots_C2_Count',
            'Children_FinalDots_C3_Count',
            'Location_Center_X',
            'Location_Center_Y']]
    if channelnumber == 3:
        return data[[
            'ObjectNumber',
            'Children_FinalDots_C2_Count',
            'Children_FinalDots_C3_Count',
            'Children_FinalDots_C4_Count',
            'Location_Center_X',
            'Location_Center_Y']]


def RabiesCP_data_reader(CPpath):
    # reads data from CellProfiler output
    # find which kind of information is in the path
    filepathsCSV = glob.glob(CPpath + '*.csv')
    filenamesCSV = [os.path.basename(i) for i in filepathsCSV]
    # check if empty
    assert len(filenamesCSV) != 0, 'No .csv files found in directory'
    # check if 'CellsAbove.csv' is in the directory and read
    assert 'CellsAbove.csv' in filenamesCSV, 'Could not find file {0}'.format('CellsAbove.csv')
    RabiesObjects = pd.read_csv(open(CPpath + 'CellsAbove.csv'))
    RabiesObjects = RabiesObjects.apply(pd.to_numeric)
    # check if 'Image.csv' is in the directory and read
    assert 'Image.csv' in filenamesCSV, 'Could not find file {0}'.format('Image.csv')
    ImageData = pd.read_csv(open(CPpath + 'Image.csv'))
    # check if 'Object relationships.csv' is in the directory and read
    assert 'Object relationships.csv' in filenamesCSV, 'Could not find file {0}'.format(
        'Object relationships.csv')
    ObjectsRel = pd.read_csv(open(CPpath + 'Object relationships.csv'))
    # check if IPO... files are there and get which values of percentile where used
    assert any(item.startswith('IPO_') for item in filenamesCSV), 'Could not find IPO_* files'
    # generate a single dataset for all
    IPOfiles = [i for i in filenamesCSV if i.startswith('IPO_')]
    cFosObjects = getDFforMultipleFiles(CPpath, IPOfiles)
    SelectedPercentiles = getSelectedPercentiles(IPOfiles)
    # create a vector with column names for selection
    SPcolnameList = ["Children_Masked_" + x + "_Count" for x in SelectedPercentiles]
    NewSPcolnameList = ["cFosPercentile_" + x + "_Object" for x in SelectedPercentiles]

    # select only important fields and rename columns
    RabiesObjects = RabiesObjects[[
        'ImageNumber',
        'ObjectNumber',
        'AreaShape_Area',
        'AreaShape_Center_X',
        'AreaShape_Center_Y',
        'Intensity_MeanIntensity_cfos',
        'Intensity_MeanIntensity_rabies'] +
        SPcolnameList]
    RabiesObjects = RabiesObjects.rename(
        columns={
            "ObjectNumber": "RabiesCellNumber",
            "AreaShape_Area": "Area",
            "AreaShape_Center_X": "Center_X",
            "AreaShape_Center_Y": "Center_Y",
            "Intensity_MeanIntensity_cfos": "MeanIntensity_cfos",
            "Intensity_MeanIntensity_rabies": "MeanIntensity_rabies"})
    for i in range(len(SPcolnameList)):
        RabiesObjects = RabiesObjects.rename(columns={SPcolnameList[i]: NewSPcolnameList[i]})

    # clean the dataset for the cfos objects
    cFosObjects = cFosObjects[[
        'ImageNumber',
        'ObjectNumber',
        'AreaShape_Area',
        'AreaShape_Center_X',
        'AreaShape_Center_Y',
        'AreaShape_Compactness',
        'AreaShape_Eccentricity',
        'PercentileInfo']]
    cFosObjects = cFosObjects.rename(columns={"ObjectNumber": "cFosObjectNumber",
                                              "AreaShape_Area": "Area",
                                              "AreaShape_Center_X": "Center_X",
                                              "AreaShape_Center_Y": "Center_Y",
                                              "AreaShape_Compactness": "Compactness",
                                              "AreaShape_Eccentricity": "Eccentricity"})
    # transform the fields in

    # merge dataset information with that of the images
    RabiesObjectsCombined = RabiesObjects.apply(getImageInfo, ImageDataFrame=ImageData, axis=1)
    cFosObjectsCombined = cFosObjects.apply(getImageInfo, ImageDataFrame=ImageData, axis=1)
    # get information related to the cFos children
    RabiesObjectsCombined = RabiesObjectsCombined.apply(
        getObjectRelationshipsInfo,
        ORDataFrame=ObjectsRel[ObjectsRel['Relationship'] == 'Parent'],
        axis=1)

    return RabiesObjectsCombined, cFosObjectsCombined


def D1D2_data_reader(CPpath):
    # reads data from CellProfiler output
    # find which kind of information is in the path
    filepathsCSV = glob.glob(CPpath + '*.csv')
    filenamesCSV = [os.path.basename(i) for i in filepathsCSV]

    # check if empty
    assert len(filenamesCSV) != 0, 'No .csv files found in directory'

    # check if 'Nuclei.csv' is in the directory and read
    co_filename = 'Nuclei.csv'
    assert co_filename in filenamesCSV, 'Could not find file {0}'.format(co_filename)
    cell_objects = pd.read_csv(open(CPpath + co_filename))
    cell_objects = cell_objects.apply(pd.to_numeric)

    # check if 'Image.csv' is in the directory and read
    id_filename = 'Image.csv'
    assert id_filename in filenamesCSV, 'Could not find file {0}'.format(id_filename)
    image_data = pd.read_csv(open(CPpath + id_filename))

    # parse the data in the title of the images to get info about the experiment in the df format
    df_parsed = image_data.apply(parse_image_info, col_name='FileName_Channel1', axis=1)

    # merge the two datasets
    df_comb = pd.merge(cell_objects, df_parsed, on='ImageNumber')

    # select and reformat the columns
    df_comb = df_comb[[
        'AnimalID',
        'ExperimentalCondition',
        'Slide',
        'Slice',
        'AP',
        'ROI',
        'ObjectNumber',
        'Children_FinalDots_C2_Count',
        'Children_FinalDots_C3_Count',
        'Location_Center_X',
        'Location_Center_Y',
        'PathName_Channel1',
        'PathName_Channel2',
        'PathName_Channel3']]

    df_comb["AnimalID"] = df_comb["AnimalID"].astype("category")
    df_comb["ExperimentalCondition"] = df_comb["ExperimentalCondition"].astype("category")
    df_comb["PathName_Channel1"] = df_comb["PathName_Channel1"].astype("category")
    df_comb["PathName_Channel2"] = df_comb["PathName_Channel2"].astype("category")
    df_comb["PathName_Channel3"] = df_comb["PathName_Channel3"].astype("category")

    return df_comb


def parse_image_info(df, col_name):
    # add columns to the dataset with information about the experiment
    # The format expected looks like this:
    # CONT01_control_slide-14_slice-1_manualROI-L-TailPosterior_squareROI-1_channel-1.tif
    name_pieces = df[col_name].split('_')
    df['AnimalID'] = name_pieces[0]
    df['ExperimentalCondition'] = name_pieces[1]
    df['Slide'] = name_pieces[2].split('-')[1]
    df['Slice'] = name_pieces[3].split('-')[1]
    df['Side'] = name_pieces[4].split('-')[1]
    df['AP'] = name_pieces[4].split('-')[2]
    df['ROI'] = name_pieces[5].split('-')[1]

    return df


def getImageInfo(df, ImageDataFrame):
    # parse the name to get metadata
    ImNameToParse = np.array(
        ImageDataFrame[ImageDataFrame['ImageNumber'] == df['ImageNumber']]['FileName_cfos'])[0]
    ImNamePieces = ImNameToParse.split('_')
    df['AnimalID'] = ImNamePieces[0]
    df['StarterCells'] = ImNamePieces[1]
    df['cFosCondition'] = ImNamePieces[2]
    df['SliceNumber'] = ImNamePieces[3]
    df['BrainSide'] = ImNamePieces[4]
    df['InjectionArea'] = 'TODO'  # TODO

    # get information regarding global image metrics and calculate relative values
    # Image_cFos_Mean = np.float(
    # ImageDataFrame[ImageDataFrame['ImageNumber']==df['ImageNumber']]['Intensity_MeanIntensity_cfos'])
    # Cell_cFos_Mean = np.float(df['Intensity_MeanIntensity_cfos'])
    # df['Relative_cFos_mean'] = (Cell_cFos_Mean/Image_cFos_Mean)

    return df


def getObjectRelationshipsInfo(df, ORDataFrame):
    # There might be an error here if a parent has two children
    # find the columns that contain children info
    ChildrenColumns = [i for i in df.index if i.startswith('cFosPercentile_')]
    # for each column, if there is a children, look into the relationships
    # dataframe for the corresponding object name
    for column in ChildrenColumns:
        if df[column] != 0:
            # find the proper relationship
            cond1 = ORDataFrame['First Object Number'] == df['RabiesCellNumber']
            cond2 = ORDataFrame['First Image Number'] == df['ImageNumber']
            SON = 'Masked_' + column.split("_")[1]
            cond3 = ORDataFrame['Second Object Name'] == SON

            df[column] = ORDataFrame[cond1 & cond2 & cond3]['Second Object Number'].values[0]

    return df


def getDFforMultipleFiles(mainpath, listOfFiles):
    # returns a combined dataframe for all the files, with an extra column
    # indicating the name of the file
    DataFrames = []
    # Read the dataframes and merge them
    for file in listOfFiles:
        df = pd.read_csv(open(mainpath + file))
        df['OrigFile'] = file
        df['PercentileInfo'] = fileToPercInfo(file)
        DataFrames.append(df)
    return pd.concat(DataFrames, ignore_index=True)


def getSelectedPercentiles(listOfFiles):
    # simple parsing of file names
    atr = []
    for file in listOfFiles:
        percUsed = file.split("_")[1]
        atr.append(percUsed)
    return atr


def fileToPercInfo(file):
    percUsed = file.split("_")[1]
    return ("cFosPercentile_" + percUsed + "_Object")
