
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
        return data[['ObjectNumber', 'Children_FinalDots_C2_Count', 'Children_FinalDots_C3_Count', 'Location_Center_X', 'Location_Center_Y']]
    if channelnumber == 3:
        return data[['ObjectNumber', 'Children_FinalDots_C2_Count', 'Children_FinalDots_C3_Count', 'Children_FinalDots_C4_Count', 'Location_Center_X', 'Location_Center_Y']]


def RabiesCP_data_reader(CPpath):
    # reads data from CellProfiler output
    # find which kind of information is in the path
    filepathsCSV = glob.glob(CPpath + '*.csv')
    filenamesCSV = [os.path.basename(i) for i in filepathsCSV]
    # check if empty
    assert len(filenamesCSV)!=0, 'No .csv files found in directory'
    # check if 'CellsAbove.csv' is in the directory and read
    assert 'CellsAbove.csv' in filenamesCSV, 'Could not find file {0}'.format('CellsAbove.csv')
    RabiesObjects = pd.read_csv(open(CPpath + 'CellsAbove.csv'))
    RabiesObjects = RabiesObjects.apply(pd.to_numeric)
    # check if 'Image.csv' is in the directory and read
    assert 'Image.csv' in filenamesCSV, 'Could not find file {0}'.format('Image.csv')
    ImageData = pd.read_csv(open(CPpath + 'Image.csv'))
    # check if 'Object relationships.csv' is in the directory and read
    assert 'Object relationships.csv' in filenamesCSV, 'Could not find file {0}'.format('Object relationships.csv')
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
    RabiesObjects = RabiesObjects[['ImageNumber', 'ObjectNumber', 'AreaShape_Area',
       'AreaShape_Center_X', 'AreaShape_Center_Y',
       'Intensity_MeanIntensity_cfos', 'Intensity_MeanIntensity_rabies'] + 
        SPcolnameList]
    RabiesObjects = RabiesObjects.rename(columns={"ObjectNumber": "RabiesCellNumber",
                                                  "AreaShape_Area": "Area",
                                                  "AreaShape_Center_X": "Center_X",
                                                  "AreaShape_Center_Y": "Center_Y",
                                                  "Intensity_MeanIntensity_cfos": "MeanIntensity_cfos",
                                                  "Intensity_MeanIntensity_rabies": "MeanIntensity_rabies"})
    for i in range(len(SPcolnameList)):
        RabiesObjects = RabiesObjects.rename(columns={SPcolnameList[i]: NewSPcolnameList[i]})
    
    # clean the dataset for the cfos objects
    cFosObjects = cFosObjects[['ImageNumber', 'ObjectNumber', 'AreaShape_Area',
       'AreaShape_Center_X', 'AreaShape_Center_Y', 'AreaShape_Compactness',
       'AreaShape_Eccentricity', 'PercentileInfo']]
    cFosObjects = cFosObjects.rename(columns={"ObjectNumber": "cFosObjectNumber",
                                              "AreaShape_Area": "Area",
                                              "AreaShape_Center_X": "Center_X",
                                              "AreaShape_Center_Y": "Center_Y",
                                              "AreaShape_Compactness": "Compactness",
                                              "AreaShape_Eccentricity": "Eccentricity"})
    # transform the fields in 

    # merge dataset information with that of the images
    RabiesObjectsCombined = RabiesObjects.apply(getImageInfo, ImageDataFrame = ImageData, axis=1)
    cFosObjectsCombined = cFosObjects.apply(getImageInfo, ImageDataFrame = ImageData, axis=1)
    # get information related to the cFos children
    RabiesObjectsCombined = RabiesObjectsCombined.apply(getObjectRelationshipsInfo,
                            ORDataFrame = ObjectsRel[ObjectsRel['Relationship']=='Parent'], axis=1)
    

    return RabiesObjectsCombined, cFosObjectsCombined


def getImageInfo(df, ImageDataFrame):
    #parse the name to get metadata
    ImNameToParse = np.array(ImageDataFrame[ImageDataFrame['ImageNumber']==df['ImageNumber']]['FileName_cfos'])[0]
    ImNamePieces = ImNameToParse.split('_')
    df['AnimalID'] = ImNamePieces[0]
    df['StarterCells'] = ImNamePieces[1]
    df['cFosCondition'] = ImNamePieces[2]
    df['SliceNumber'] = ImNamePieces[3]
    df['BrainSide'] = ImNamePieces[4]
    df['InjectionArea'] = 'TODO' #change this
        
    #get information regarding global image metrics and calculate relative values
    #Image_cFos_Mean = np.float(ImageDataFrame[ImageDataFrame['ImageNumber']==df['ImageNumber']]['Intensity_MeanIntensity_cfos'])
    #Cell_cFos_Mean = np.float(df['Intensity_MeanIntensity_cfos'])
    #df['Relative_cFos_mean'] = (Cell_cFos_Mean/Image_cFos_Mean)
    
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