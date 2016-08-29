"""
Given a set of .csv files with data for each biweekly period in the year,
remap the fields provide only the biweekly periods leading up to the
observation date.

Currently only processes the TRMM 3B42 precipitation and MODIS clear sky days
fields. Fields to be revisited once we have TRMM 3B43, GMM, and CFSR data.
"""

import pandas as pd
import re


def get_leading_data(biweeks_lead, base_biweek,
                     col_names, field_prefix=None, field_suffix=None):
    biweek_re = re.compile('_\d{2}_')
    if field_prefix is not None:
        col_names = [x for x in col_names if
                     biweek_re.split(x)[0] == field_prefix]
    if field_suffix is not None:
        col_names = [x for x in col_names if
                     biweek_re.split(x)[-1] == field_suffix]
    if field_prefix is None and field_suffix is None:
        return None
    # [1:3] in tag below extracts the biweek number from a string like
    # _24_
    return [x for x in col_names if
            int(biweek_re.findall(x)[0][1:3]) == (base_biweek - biweeks_lead)][0]


def load_base_table(sat_data_files):
    """
    Load the survey data, join it with the satellite data, add
    perform some basic preproccessing.
    """
    df = pd.read_csv("RustSurvey.csv")
    df = df.set_index('Location.ID')

    for path in sat_data_files:
        temp = pd.read_csv(path)
        temp = temp.set_index('Location.ID')
        df = df.join(temp)

    df['StemOrYellowBinary'] = df['StemRust.Binary'] | df['YellowRust.Binary']
    df['ObsDate'] = pd.to_datetime(df.ObsDate)
    df['ObsMonth'] = df['ObsDate'].apply(lambda x: x.month)
    df['coords'] = df[['Latitude', 'Longitude']].apply(tuple, axis=1)
    df['BiWeekNum'] = df.ObsDate.apply(
        lambda x: x.month*2 - 1 + 1*(x.day >= 15))
    """
    Drop first half of the year as we have no way of wrapping from
    (for example) Jan 2015 to 2014.
    """
    df = df[df.BiWeekNum > 12]
    return df


if __name__ == '__main__':
    sat_data_files = ["TRMM_3B42.csv", "MODIS_MYD11A2.csv",
                      "MODIS_MOD13Q1.csv"]
    df = load_base_table(sat_data_files)
    biweek_re = re.compile('_\d{2}_')
    """
    Run the line below to get a rough list of the major fields:
    major_fields = sorted(list(set([biweek_re.split(x)[-1] for x in df.columns])))
    """
    biweeks_lead_max = 6
    field_suffixes_to_process = ['precipitation', 'Clear_sky_days']
    col_names = df.columns
    for field in field_suffixes_to_process:
        for i in xrange(1, biweeks_lead_max+1):
            df[field+'_leading_'+str(i)] = df.apply(lambda x:
                x[get_leading_data(i, x.BiWeekNum, col_names, field_suffix=field)], axis=1)
        df.drop([x for x in df.columns if biweek_re.split(x)[-1] == field],
                inplace=True, axis=1)
    print "Dataframe loaded"
