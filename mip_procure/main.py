
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
    demands = dict(zip(zip(dat.demand_packing['Packing ID'], dat.demand_packing['Period ID']), dat.demand_packing['Demand']))
    min_inventory = dict(zip(zip(dat.inventory['Factory ID'], dat.inventory['Packing ID']), dat.inventory['Minimum Inventory']))
    ini_inventory = dict(zip(zip(dat.inventory['Factory ID'], dat.inventory['Packing ID']), dat.inventory['Initial Inventory']))
    unit_price = dict(zip(dat.packing['Packing ID'], dat.packing['Unit Price']))
    inven_cost = dict(zip(zip(dat.inventory['Factory ID'], dat.inventory['Packing ID']), dat.inventory['Inventory Cost']))
    acquisition_limit_period = dict(zip(zip(dat.demand_packing['Packing ID'], dat.demand_packing['Period ID']),
                                        dat.demand_packing['Acquisition Limit Period']))
    transport_limit_period = dict(zip(zip(dat.demand_packing['Packing ID'], dat.demand_packing['Period ID']),
                                      dat.demand_packing['Transport Limit Period']))
    print(inven_cost)
    print(unit_price)
    print(min_inventory)
    print(demands)
    print('params:\n', params)  #It's just a test


    #Build optimization model
    mdl = pulp.LpProblem('PetGourmet', sense=pulp.LpMinimize) #Define the model
    keys = [(i, t) for i in I for t in T]
    keys_extended = [(i, t) for i in I for t in T_extended]
    y = pulp.LpVariable.dicts(indices=keys_extended, cat=pulp.LpInteger, lowBound=0.0, name='y')  # Qty  in Patas Pack
    z = pulp.LpVariable.dicts(indices=keys_extended, cat=pulp.LpInteger, lowBound=0.0, name='z')  # Qty  in Pet Gourmet
    x = pulp.LpVariable.dicts(indices=keys, cat=pulp.LpInteger, lowBound=0.0, name='x')  # Qty of transporting packing
    w = pulp.LpVariable.dicts(indices=keys, cat=pulp.LpInteger, lowBound=0.0, name='w')  # Acquired quantity of packing

    # Constraints:
    # C1) Inventory capacity:
    for t in T:
        # Patas Pack Inventory Capacity
        mdl.addConstraint(lpSum(y[i, t] for i in I) <= params['InventoryCapacityPack'], name=f'C1a_{t}')
        # Pet Gourmet Inventory Capacity
        mdl.addConstraint(lpSum(z[i, t] for i in I) <= params['InventoryCapacityGourmet'], name=f'C1b_{t}')

    # C2) Acquisition limit of packing in by period:
    for i in I:
        for t in T:
            mdl.addConstraint(w[i, t] <= acquisition_limit_period[i, t])

    # C3) Transporting limit by period
    for i in I:
        for t in T:
            mdl.addConstraint(x[i, t]  <= transport_limit_period[i, t])
    # TODO: Não pode depender da embalagem.

    # C4) Flow Balance constraint:
    for t in T:
        for i in I:
            mdl.addConstraint(z[i, t] == z[i, t - 1] + x[i, t] - demands[i, t], name=f'C4a_{t}_{i}')
            mdl.addConstraint(y[i, t] == y[i, t - 1] + w[i, t] - x[i, t], name=f'C4b_{t}_{i}')      #New constraint, necessary to add to formulation

    # C5) Minimum Inventory constraint:
    for t in T:
        for i in I:
            mdl.addConstraint(z[i, t] >= min_inventory['Gourmet', i], name=f'C5_{t}_{i}')

    # C6) Maximum time in Patas Pack constraint:
    for t in T:
        if t <= max(T) - params['MaxTimePackingPack']:
            for i in I:
                mdl.addConstraint(lpSum(x[i, t + l] for l in range(1, params['MaxTimePackingPack'] + 1)) >= y[i, t], name=f'C6_{t}_{i}')

    # C7) Initial Inventory Constraint:
    for i in I:
        mdl.addConstraint(y[i, first_period - 1] == ini_inventory['Pack', i], name=f'C7a_{i}')
        mdl.addConstraint(z[i, first_period - 1] == ini_inventory['Gourmet', i], name=f'C7b_{i}')

    # end constraint's region


    #Set Objective Function
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
        print('x:\n', x_sol)
        print('y:\n', y_sol)
        print('w:\n', w_sol)
        print('z:\n', z_sol)


    else:
        x_sol = None
        print(f'Model is not optimal. Status: {status}')

    # Populate output schema
    sln = output_schema.PanDat()

    if status == 'Optimal':

        w_df = pd.DataFrame(w_sol, columns=['Packing ID', 'Period ID', 'Acquired Quantity'])
        x_df = pd.DataFrame(x_sol, columns=['Packing ID', 'Period ID', 'Transferred Quantity'])
        z_df = pd.DataFrame(z_sol, columns=['Packing ID', 'Period ID', 'Final Inventory'])

        #demand table
        demand_packing_df = pd.read_csv('data/inputs/demand_packing.csv')
        demand_df = demand_packing_df[['Packing ID', 'Period ID', 'Demand']]

        #Pet Gourmet Table
        z2_df = demand_df.merge(z_df, on=['Packing ID', 'Period ID'], how='left')
        z2_df['Initial Inventory'] = z2_df['Demand'] + z2_df['Final Inventory']
        new_order = ['Packing ID', 'Period ID', 'Initial Inventory', 'Demand', 'Final Inventory']
        z2_df = z2_df[new_order]
        sln.pet_gourmet = z2_df

        # Patas Pack Table
        y_df = pd.DataFrame(y_sol, columns=['Packing ID', 'Period ID', 'Final Inventory'])
        y2_df = x_df.merge(y_df, on=['Packing ID', 'Period ID'], how='left')
        y2_df['Initial Inventory'] = y2_df['Transferred Quantity'] + y2_df['Final Inventory']
        new_order = ['Packing ID', 'Period ID', 'Initial Inventory', 'Transferred Quantity', 'Final Inventory']
        y2_df = y2_df[new_order]
        sln.patas_pack = y2_df

        # Acquisition by period table
        acquisition_df = w_df.merge(x_df, on=['Packing ID', 'Period ID'], how='left')
        sln.acquisition_by_period = acquisition_df

        return print(sln.pet_gourmet), print('\n', sln.acquisition_by_period), print('\n', sln.patas_pack)


