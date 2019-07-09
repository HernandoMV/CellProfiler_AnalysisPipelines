
import pandas as pd


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


def RabiesCP_data_reader(CAfile, IMfile):
    # reads data from CellProfiler output CellsAbove.csv and Image.csv

    # read data into a dataframe where each entry is the cell number
    CAdata = pd.read_csv(open(CAfile))
    assert isinstance(CAdata, object)
    
    IMdata = pd.read_csv(open(IMfile))
    assert isinstance(IMdata, object)

    # select only important fields
    CAdata = CAdata.apply(pd.to_numeric)
    CAdata = CAdata[['ImageNumber', 'ObjectNumber', 'AreaShape_Area', 'AreaShape_Center_X',
       'AreaShape_Center_Y',
       'Intensity_IntegratedIntensity_cfos',
       'Intensity_IntegratedIntensity_rabies',
       'Intensity_MaxIntensity_cfos', 'Intensity_MaxIntensity_rabies',
       'Intensity_MeanIntensity_cfos', 'Intensity_MeanIntensity_rabies', 
       'Intensity_MedianIntensity_cfos', 'Intensity_MedianIntensity_rabies', 
       'Intensity_StdIntensity_cfos', 'Intensity_StdIntensity_rabies']]
    IMdata = IMdata[['Count_CellsAbove', 'FileName_cfos', 'ImageNumber',
       'Intensity_MeanIntensity_cfos', 'Intensity_MeanIntensity_rabies',
       'Intensity_MedianIntensity_cfos', 'Intensity_MedianIntensity_rabies',
       'Intensity_StdIntensity_cfos', 'Intensity_StdIntensity_rabies',]]

    return CAdata, IMdata