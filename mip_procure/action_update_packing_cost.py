def update_packing_cost_solve(dat):
    """Increases packing cost by 20%"""
    packing = dat.packing.copy()
    packing['Unit Price'] = 1.2 * packing['Unit Price']
    packing = packing.round({'Unit Price': 2})
    dat.packing = packing[['Packing ID', 'Unit Price', 'Size', 'Color']]
    return dat


from mip_procure import input_schema


def update_packing_cost_solve2(dat):
    """Multiply packing cost by the Packing Cost Multiplier parameter"""
    params = input_schema.create_full_parameters_dict(dat)
    packing = dat.packing.copy()
    packing['Unit Price'] = params['Packing Cost Multiplier'] * packing['Unit Price']
    packing = packing.round({'Unit Price': 2})
    dat.packing = packing
    return dat

