import numpy as np
# import pandas as pd


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
        shuffledIdx = df[np.logical_and(df[sc] >= tr[0], df[sc] < tr[1])].index.values
        # shuffle them
        np.random.shuffle(shuffledIdx)
        # append, else append empty
        if len(shuffledIdx) > 0:
            indexes.append(list(shuffledIdx[0:n]))
        else:
            indexes.append([])

    return(indexes)
