
def concat_int_cols(df, col1, col2, fill1=2, fill2=5, return_col='PUMA_GEOID'):
    """ Concatenate two integer columns using zfill """
    df[[col1, col2]] = df[[col1, col2]].astype(str)
    df[col1] = df[col1].str.zfill(fill1)
    df[col2] = df[col2].str.zfill(fill2)
    df[return_col] = df[col1] + df[col2]
    df[[col1, col2, return_col]] = df[[col1, col2, return_col]].astype(int)
    return df
