# reads data from CellProfiler output Nuclei.csv
import pandas as pd


def data_reader(file, channelnumber):

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


