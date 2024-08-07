from pathlib import Path
import pandas as pd
from mip_procure import input_schema

pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 4000)

cwd = Path(__file__).parent.resolve()

# Read input data
input_path = cwd / 'data/inputs'
dat = input_schema.csv.create_pan_dat(input_path)


def data_integrity_checks(dat):
    # ensure that all packing share the same time horizon in demand packing.
    demand_packing_df = dat.demand_packing.copy()
    grouped = demand_packing_df.groupby('Packing ID')['Period ID'].apply(set)
    packing = set(demand_packing_df['Packing ID'])
    for i in packing:
        for j in packing:
            if grouped[i] != grouped[j]:
                raise ValueError("There are packing with different time horizon in demand packing.")
    return





