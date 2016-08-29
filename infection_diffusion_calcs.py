"""
Calculates metrics regarding the distance between rust infections
in one year and the next.

User must update the RustSurvey.csv file path efore running.

TODO: exclude points with no samples at all within radius N
TODO: # next year infections within radius N
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from geopy.distance import great_circle
from copy import deepcopy


def get_nearest_neighbors(tgt_coords, metadata_df, k):
    """
    Give a dataframe of coordinates and a set of target coordinates,
    returns a list of the pairwise distances.
    """
    df = deepcopy(metadata_df)
    df['coord_pairs'] = df.coords.apply(lambda x: tuple([tgt_coords, x]))
    df['dists'] = df.coord_pairs.apply(lambda x: great_circle(*x).miles)
    df = df[df.dists.isin(df.dists.nsmallest(k))]
    results = zip(df.index.values.tolist(), df.dists.values.tolist())
    results.sort(key=lambda x: x[1])
    # have to use set to drop duplicate distances
    return list(set([x[1] for x in results]))


def get_dists_for_yr(year, filter_col):
    tgt_yr_df = df[(df.ObsYear == year) & df[filter_col]]
    next_yr_df = df[(df.ObsYear == year+1) & df[filter_col]]
    return tgt_yr_df.coords.apply(
        lambda x: get_nearest_neighbors(x, next_yr_df, 1))


def unpack(lst):
    """
    Unpacks the first item of the list, if it exists
    """
    try:
        return lst[0]
    except:
        return np.nan


def count_within_radius(dists, radius):
    return len([x for x in dists if x <= radius])


def get_med_dist_to_next_infection(rust_nm):
    df.dropna(subset=['coords'], inplace=True)
    # ignore 2015 as 2016 has very limited data to scan forward to
    yrs_to_scan = [i for i in xrange(2007, 2015)]
    dists = {year: get_dists_for_yr(year, rust_nm+'.Binary')
             for year in yrs_to_scan}
    radii = []
    for yr in dists:
        radii.extend([count_within_radius(x, 10) for x in dists[yr]])
        dists[yr] = dists[yr].apply(lambda x: unpack(x))
        dists[yr].dropna(inplace=True)
    report = "Median distance between a "+rust_nm+" infection and the closest"
    report += " infection in the next year is {0} miles"
    dists = pd.concat(dists.values())
    print(report.format(int(dists.median())))
    return dists, radii


if __name__ == '__main__':
    survey_nm = "/Users/sohier/Desktop/Gates_Plant_Rust/RustSurvey.csv"
    survey = pd.read_csv(survey_nm)
    df = survey
    df.drop_duplicates(subset=['ObsDate', 'Latitude', 'Longitude'],
                       inplace=True)
    df['StemOrYellowBinary'] = df['StemRust.Binary'] | df['YellowRust.Binary']
    df['ObsDate'] = pd.to_datetime(df.ObsDate)
    df['ObsMonth'] = df['ObsDate'].apply(lambda x: x.month)
    df['coords'] = df[['Latitude', 'Longitude']].apply(tuple, axis=1)
    stem_rust_data = get_med_dist_to_next_infection('StemRust')
    yellow_rust_data = get_med_dist_to_next_infection('YellowRust')

    stem_rust_dists = stem_rust_data[0]
    yellow_rust_dists = yellow_rust_data[0]
    stem_rust_radii = stem_rust_data[1]
    yellow_rust_radii = yellow_rust_data[1]
    print("Median stem rust radii: "+str(np.median(stem_rust_radii)))
    print("Median yellow rust radii: "+str(np.median(yellow_rust_radii)))
    plt.plot([float(i)/len(stem_rust_dists) for i in xrange(len(stem_rust_dists))],
             sorted(stem_rust_dists))
    plt.ylabel('Miles to Nearest Infection In Following Year')
    plt.xlabel('Occurrence Percentile')
    plt.axhline(y=10)
    plt.title('Stem Rust Infections With Follow Up Infections Within Walking Distance')
    plt.show()

    plt.plot([float(i)/len(stem_rust_dists) for i in xrange(len(yellow_rust_dists))],
             sorted(yellow_rust_dists))
    plt.ylabel('Miles to Nearest Infection In Following Year')
    plt.xlabel('Occurrence Percentile')
    plt.axhline(y=10)
    plt.title('Yellow Rust Infections With Follow Up Infections Within Walking Distance')
    plt.show()
