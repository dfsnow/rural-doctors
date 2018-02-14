import config
import utils
import pandas as pd
import puma_functions as pf
import glob
import os
import re


def acs_filter(df):
    """ Filter IPUMS dataset with the listed filters"""
    df = df[
        (df['YEAR'] > 2011) &  # Census year after 2011
        (df['AGE'] >= 25) &  # Older than 25, no fake docs
        (df['UHRSWORK'] >= 30) &  # Only doctors who are actually working
        # (df['EDUCD'] == 116) &  # Only doctors with a masters or higher
        (df['STATEFIP'] != 72)]  # Get outta here Puerto Rico
    return df


def acs_reduce(df):
    """ Keep only OCC2010 codes which are in the config file """
    df_reduced = df[
        df[config.acs_occ_var].isin(config.acs_occ_dict.keys())].reset_index()
    return df_reduced


def acs_split(df, path='data/'):
    """ Split ACS file into separate CSVs by OCC2010 code """
    gb = df.groupby(config.acs_occ_var)
    [gb.get_group(occ).to_csv(
        os.path.join(path, '{y_min}-{y_max}_acs_{x}.csv'.format(
            y_min=min(df['YEAR']),
            y_max=max(df['YEAR']),
            x=config.acs_occ_dict[occ])),
        index=False) for occ in gb.groups]


def acs_unsplit(path='data/'):
    """
    Concatenate split ACS files back into single CSV
    """
    files = [glob.glob(path + '*acs_{x}.csv'.format(x=occ))
             for occ in list(config.acs_occ_dict.values())]
    print(files)
    df = pd.concat((pd.read_csv(f[0]) for f in files), ignore_index=True)
    return df


def acs_counts(df):
    """ Reduce ACS file into total counts and fraction of OCC2010 codes """
    data = utils.concat_int_cols(df, 'STATEFIP', 'PUMA')
    n_occ = data[config.acs_occ_var].nunique()

    if n_occ > 1:
        counts = data.groupby(['PUMA_GEOID', config.acs_occ_var])\
            .sum()['PERWT']\
            .unstack(config.acs_occ_var)\
            .reset_index()
        counts = counts.rename(columns=config.acs_occ_dict)
    else:
        occ_name = config.acs_occ_dict[data[config.acs_occ_var].unique()[0]]
        counts = data.groupby(['PUMA_GEOID']).sum()['PERWT'].reset_index()
        counts = counts.rename(columns={'PERWT': occ_name})

    pop = pf.get_puma_pop()
    data = counts.merge(pop, how='left', on='PUMA_GEOID')

    if n_occ > 1:
        for occ in config.acs_occ_dict.values():
            data[occ] = data[occ] / df['YEAR'].nunique()
            data[occ + '_FRAC'] = data[occ] / data['POP']
            data[occ + '_PER_100K'] = data[occ + '_FRAC'] * 1e5
    else:
        data[occ_name] = data[occ_name] / df['YEAR'].nunique()
        data[occ_name + '_FRAC'] = data[occ_name] / data['POP']
        data[occ_name + '_PER_100K'] = data[occ_name + '_FRAC'] * 1e5

    data = data.fillna(0)
    return data


def acs_process(csv, path='data/'):
    """ Wrapper function for running all others in sequence """
    df = pd.read_csv(os.path.join(path, csv))
    acs_split(df, path=path)
    files = [glob.glob(path + '*acs_{x}.csv'.format(x=occ))
             for occ in list(config.acs_occ_dict.values())]
    for f in files:
        print(str(f[0]))
        if bool(re.search('PHYS', f[0])):
            data = pd.read_csv(f[0])
            data = acs_filter(data)
            data = acs_counts(data)
            data.to_csv(os.path.join(path, '{y_min}-{y_max}_acs_{x}_counts.csv'.format(
                y_min=min(df['YEAR']),
                y_max=max(df['YEAR']),
                x=re.sub('[^A-Z]', '', f[0]))),
                index=False)
        else:
            data = pd.read_csv(f[0])
            data = acs_counts(data)
            data.to_csv(os.path.join(path, '{y_min}-{y_max}_acs_{x}_counts.csv'.format(
                y_min=min(df['YEAR']),
                y_max=max(df['YEAR']),
                x=re.sub('[^A-Z]', '', f[0]))),
                index=False)


