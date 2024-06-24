from mip_procure.schemas import input_schema, output_schema
import pulp
from pulp import lpSum
import pandas as pd

def solve(dat):
    # Prepare optimization parameters
    I = set(dat.packing['Packing ID'])
    J = set(dat.inventory['Factory ID'])
    T = set(dat.demand_packing['Period ID'])
    first_period = min(T)
    T_extended = T.union({first_period -1})
    params = input_schema.create_full_parameters_dict(dat)
    demands = dict(zip(zip(dat.demand_packing['Packing ID'], dat.demand_packing['Period ID']),
                       dat.demand_packing['Demand']))
    min_inventory = dict(zip(zip(dat.inventory['Factory ID'], dat.inventory['Packing ID']),
                             dat.inventory['Minimum Inventory']))
    ini_inventory = dict(zip(zip(dat.inventory['Factory ID'], dat.inventory['Packing ID']),
                             dat.inventory['Initial Inventory']))
    unit_price = dict(zip(dat.packing['Packing ID'], dat.packing['Unit Price']))
    inven_cost = dict(zip(zip(dat.inventory['Factory ID'], dat.inventory['Packing ID']),
                          dat.inventory['Inventory Cost']))
    acquisition_limit_period = dict(zip(zip(dat.demand_packing['Packing ID'], dat.demand_packing['Period ID']),
                                        dat.demand_packing['Acquisition Limit Period']))
    acquisition_min_period = dict(zip(zip(dat.demand_packing['Packing ID'], dat.demand_packing['Period ID']),
                                        dat.demand_packing['Acquisition Min Period']))

    # Build optimization model
    mdl = pulp.LpProblem('PetGourmet', sense=pulp.LpMinimize)  # Define the model
    keys = [(i, t) for i in I for t in T]
    keys_extended = [(i, t) for i in I for t in T_extended]
    y = pulp.LpVariable.dicts(indices=keys_extended, cat=pulp.LpInteger, lowBound=0.0, name='y')  # Qty  in Patas Pack
    z = pulp.LpVariable.dicts(indices=keys_extended, cat=pulp.LpInteger, lowBound=0.0, name='z')  # Qty  in Pet Gourmet
    x = pulp.LpVariable.dicts(indices=keys, cat=pulp.LpInteger, lowBound=0.0, name='x')  # Qty of transporting packing
    w = pulp.LpVariable.dicts(indices=keys, cat=pulp.LpInteger, lowBound=0.0, name='w')  # Acquired quantity of packing
    wb = pulp.LpVariable.dicts(indices=keys, cat=pulp.LpBinary, name='wb') # Binary decision variable of acquisition

    # Constraints:

    # C1) Inventory capacity:
    for t in T:
        # Patas Pack Inventory Capacity
        mdl.addConstraint(lpSum(y[i, t] for i in I) <= params['InventoryCapacityPack'], name=f'C1a_{t}')
        # Pet Gourmet Inventory Capacity
        mdl.addConstraint(lpSum(z[i, t] for i in I) <= params['InventoryCapacityGourmet'], name=f'C1b_{t}')

    # C2) Acquisition limit of packing i by period:
    for i in I:
        for t in T:
            mdl.addConstraint(w[i, t] <= wb[i, t]*acquisition_limit_period[i, t], name=f'C2_{t}_{i}')

    # C3) Transporting limit by period
    for t in T:
        mdl.addConstraint(lpSum(x[i,t] for i in I) <= params['TransportingLimitByPeriod'], name=f'C3_{t}')

    # C4) Flow Balance constraint:
    for t in T:
        for i in I:
            mdl.addConstraint(z[i, t] == z[i, t - 1] + x[i, t] - demands[i, t], name=f'C4a_{t}_{i}')
            mdl.addConstraint(y[i, t] == y[i, t - 1] + w[i, t] - x[i, t], name=f'C4b_{t}_{i}')

    # C5) Minimum Inventory constraint:
    for t in T:
        for i in I:
            mdl.addConstraint(z[i, t] >= min_inventory['Gourmet', i], name=f'C5_{t}_{i}')

    # C6) Maximum time in Patas Pack constraint:
    for t in T:
        if t <= max(T) - params['MaxTimePackingPack']:
            for i in I:
                mdl.addConstraint(lpSum(x[i, t + l] for l in range(1, params['MaxTimePackingPack'] + 1)) >= y[i, t],
                                  name=f'C6_{t}_{i}')

    # C7) Initial Inventory Constraint:
    for i in I:
        mdl.addConstraint(y[i, first_period - 1] == ini_inventory['Pack', i], name=f'C7a_{i}')
        mdl.addConstraint(z[i, first_period - 1] == ini_inventory['Gourmet', i], name=f'C7b_{i}')

    # C8) Minimum of acquisition of a packing:
    for i in I:
        for t in T:
            w[i, t] >= wb[i ,t]*acquisition_min_period[i,t]

    # end constraint's region

    # Set Objective Function
    mdl.setObjective(
        lpSum(unit_price[i] * w[i, t] for i in I for t in T) +
        lpSum(inven_cost['Pack', i] * y[i, t] for i in I for t in T) +
        lpSum(inven_cost['Gourmet', i] * z[i, t] for i in I for t in T)
    )

    # Optimize and retrieve the solution
    mdl.writeLP('model.lp')
    mdl.solve()
    status = pulp.LpStatus[mdl.status]

    if status == 'Optimal':
        x_sol = [(i, t, var.value()) for (i, t), var in x.items()]
        y_sol = [(i, t, var.value()) for (i, t), var in y.items()]
        z_sol = [(i, t, var.value()) for (i, t), var in z.items()]
        w_sol = [(i, t, var.value()) for (i, t), var in w.items()]
        wb_sol = [(i, t, var.value()) for (i, t), var in wb.items()] #without future use

    else:
        x_sol = None
        print(f'Model is not optimal. Status: {status}')

    # Populate the output schema
    sln = output_schema.PanDat()

    if status == 'Optimal':
        w_df = pd.DataFrame(w_sol, columns=['Packing ID', 'Period ID', 'Acquired Quantity'])
        x_df = pd.DataFrame(x_sol, columns=['Packing ID', 'Period ID', 'Transferred Quantity'])
        z_df = pd.DataFrame(z_sol, columns=['Packing ID', 'Period ID', 'Final Inventory'])

        # demand table
        demand_packing_df = dat.demand_packing.copy()
        demand_df = demand_packing_df[['Packing ID', 'Period ID', 'Demand']]

        # Pet Gourmet Table
        pet_gourmet_df = x_df.merge(z_df, on=['Packing ID', 'Period ID'], how='left')
        pet_gourmet_df = demand_df.merge(pet_gourmet_df, on=['Packing ID', 'Period ID'], how='right')
        # if demand wasn't specified then we don't have demand.
        pet_gourmet_df['Demand'] = pet_gourmet_df['Demand'].fillna(0)
        pet_gourmet_df['Initial Inventory'] = (pet_gourmet_df['Demand'] + pet_gourmet_df['Final Inventory']
                                               - pet_gourmet_df['Transferred Quantity'])
        new_order = ['Packing ID', 'Period ID', 'Initial Inventory', 'Demand',
                     'Transferred Quantity', 'Final Inventory' ]
        pet_gourmet_df = pet_gourmet_df[new_order]
        pet_gourmet_df = pet_gourmet_df.sort_values(by=['Packing ID', 'Period ID'],
                                                    ascending=[True, True], ignore_index=True)
        sln.pet_gourmet = pet_gourmet_df

        # Patas Pack Table
        y_df = pd.DataFrame(y_sol, columns=['Packing ID', 'Period ID', 'Final Inventory'])
        patas_pack_df = x_df.merge(y_df, on=['Packing ID', 'Period ID'], how='left')
        patas_pack_df = patas_pack_df.merge(w_df, on=['Packing ID', 'Period ID'], how='left')
        # y[i, t] == y[i, t - 1] + w[i, t] - x[i, t] remember the flow balance's equation
        patas_pack_df['Initial Inventory'] = (patas_pack_df['Transferred Quantity'] +
                                              patas_pack_df['Final Inventory'] - patas_pack_df['Acquired Quantity'])
        new_order = ['Packing ID', 'Period ID', 'Initial Inventory', 'Transferred Quantity',
                     'Acquired Quantity', 'Final Inventory']
        patas_pack_df = patas_pack_df[new_order]
        patas_pack_df = patas_pack_df.sort_values(by=['Packing ID', 'Period ID'],
                                                  ascending=[True, True], ignore_index=True)
        sln.patas_pack = patas_pack_df

    return sln


