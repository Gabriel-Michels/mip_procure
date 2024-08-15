import itertools


def data_integrity_checks(dat):
    demand_packing_df = dat.demand_packing.copy()
    periods_set = set(range(demand_packing_df['Period ID'].min(), demand_packing_df['Period ID'].max() + 1))
    packings_set = set(dat.packing['Packing ID'])
    set_packing_periods = set(itertools.product(packings_set, periods_set))
    set_received = set(zip(demand_packing_df['Packing ID'], demand_packing_df['Period ID']))
    set_dif = set_packing_periods.difference(set_received)
    if set_dif != set():
        raise ValueError(f'There are missing pairs of packing and period from demand_packing:\n'
                         f'{set_dif}')
    return


def data_integrity_checks2(dat):
    packings_set = set(dat.packing['Packing ID'])
    factories_set = set(dat.inventory['Factory ID'])
    set_factories_packings = set(itertools.product(factories_set, packings_set))
    set_received = set(zip(dat.inventory['Factory ID'], dat.inventory['Packing ID']))
    set_dif = set_factories_packings.difference(set_received)
    if set_dif != set():
        raise ValueError(f'There are missing pairs od factory and product from inventory tablr:\n'
                         f'{set_dif}')
    return


def data_integrity_checks3(dat):
    packings_set = set(dat.packing['Packing ID'])
    set_received = set(dat.items_aging['Packing ID'])
    set_dif = packings_set.difference(set_received)
    if set_dif != set():
        raise ValueError(f'There are missing packing in the table items_aging:'
                         f'{set_dif}')
    return


def data_integrity_checks4(dat):
    packings_set = set(dat.packing['Packing ID'])
    set_received = set(dat.distribution['Packing ID'])
    set_dif = packings_set.difference(set_received)
    if set_dif != set():
        raise ValueError(f'There are missing some packing from distribution table \n'
                         f'{set_dif}')
    return




