from parceltrack.configs.paths import ProjectPaths
from parceltrack.io import (load_processed_year_files) 

import pandas as pd
import geopandas as gpd
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)


if __name__ == '__main__':
    paths = ProjectPaths()

    parcels_2021 = load_processed_year_files(directory=paths.processed, year=2021)
    print(type(parcels_2021), parcels_2021.shape)
    parcel_columns = parcels_2021.columns.tolist()
    columns = ['ACCTID', 'OWNNAME1', 'ADDRESS', 'BLOCK', 'ZONING', 'YEARBLT', 'SQFTSTRC', 'NFMLNDVL', 'NFMIMPVL', 'NFMTTLVL', 'geometry']
    parcels_2021_subset = parcels_2021[columns].copy()
    zones = parcels_2021_subset['ZONING'].value_counts(dropna=False)
    
    zero_val = parcels_2021_subset[parcels_2021_subset['NFMTTLVL']==0]
    zero_val_owners = zero_val['OWNNAME1'].value_counts(dropna=False)

    weird_zero_value = zero_val[zero_val['SQFTSTRC'] > 0].copy()
    print(weird_zero_value[['ACCTID', 'OWNNAME1', 'ADDRESS', 'ZONING', 'YEARBLT', 'SQFTSTRC']])
    print(weird_zero_value['OWNNAME1'].value_counts())
    print(weird_zero_value['ZONING'].value_counts())
