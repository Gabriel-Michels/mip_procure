from mip_procure import input_schema

def update_packing_cost_solve(dat):
    """Multiply packing cost by the Packing Cost Multiplier parameter"""
    params = input_schema.create_full_parameters_dict(dat)
    packing = dat.packing.copy()
    packing['Unit Price'] = params['Packing Cost Multiplier'] * packing['Unit Price']
    packing = packing.round({'Unit Price': 2})
    dat.packing = packing
    return dat

