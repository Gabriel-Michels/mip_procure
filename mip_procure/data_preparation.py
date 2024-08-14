import itertools


def data_integrity_checks(dat):
    demand_packing_df = dat.demand_packing.copy()
    periods_set = set(range(demand_packing_df['Period ID'].min(), demand_packing_df['Period ID'].max() + 1))
    packings_set = set(demand_packing_df['Packing ID'])
    set_packing_periods = set(itertools.product(packings_set, periods_set))
    set_received = set(zip(demand_packing_df['Packing ID'], demand_packing_df['Period ID']))
    set_dif = set_packing_periods.difference(set_received)
    if set_dif != set():
        raise ValueError(f'There are missing pairs of packing and period from demand_packing:\n'
                         f'{set_dif}')
    return
