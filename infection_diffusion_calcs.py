"""
Calculates metrics regarding the distance between rust infections
in one year and the next.

Tasks:
TODO: exclude points with no samples at all within radius N?
TODO: # next year infections within radius N
TODO: multiple lines, one plot
"""

import pandas as pd
import numpy as np
from geopy.distance import great_circle
from copy import deepcopy


def get_nearest_neighbors(tgt_coords, metadata_df, k, min_distance=10):
    """
    Give a dataframe of coordinates and a set of target coordinates,
    returns a list of the pairwise haversine distances between stations.
    """
    df = deepcopy(metadata_df)
    df['coord_pairs'] = df.coords.apply(lambda x: tuple([tgt_coords, x]))
    df['dists'] = df.coord_pairs.apply(lambda x: great_circle(*x).miles)
    df = df[df['dists'] > min_distance]
    df = df[df.dists.isin(df.dists.nsmallest(k))]
    results = zip(df.index.values.tolist(), df.dists.values.tolist())
    results.sort(key=lambda x: x[1])
    # have to use set to drop duplicate distances
    return list(set([x[1] for x in results]))


def get_dists_for_yr(year, filter_col):
    tgt_yr_df = df[(df.ObsYear == year) & df[filter_col]]
    next_yr_df = df[(df.ObsYear == year+1) & df[filter_col]]
    return tgt_yr_df.coords.apply(
        lambda x: get_nearest_neighbors(x, next_yr_df, 1, -1))


def unpack(lst):
    try:
        return lst[0]
    except:
        return np.nan


def get_med_dist_to_next_infection(rust_nm):
    df.dropna(subset=['coords'], inplace=True)
    yrs_to_scan = sorted(df.ObsYear.unique())[:-1]
    dists = {year: get_dists_for_yr(year, rust_nm+'.Binary')
             for year in yrs_to_scan}
    for yr in dists:
        dists[yr] = dists[yr].apply(lambda x: unpack(x))
        dists[yr].dropna(inplace=True)
    report = "Median distance between a "+rust_nm+" infection and the closest"
    report += " infection in the next year is {0} miles"
    dists = pd.concat(dists.values())
    print(report.format(int(dists.median())))
    return dists


if __name__ == '__main__':
    survey_nm = "/Users/sohier/Desktop/Gates_Plant_Rust/RustSurvey.csv"
    survey = pd.read_csv(survey_nm)
    df = survey
    df['StemOrYellowBinary'] = df['StemRust.Binary'] | df['YellowRust.Binary']
    df['ObsDate'] = pd.to_datetime(df.ObsDate)
    df['ObsMonth'] = df['ObsDate'].apply(lambda x: x.month)
    df['coords'] = df[['Latitude', 'Longitude']].apply(tuple, axis=1)
    stem_dists = get_med_dist_to_next_infection('StemRust')
    yellow_dists = get_med_dist_to_next_infection('YellowRust')
