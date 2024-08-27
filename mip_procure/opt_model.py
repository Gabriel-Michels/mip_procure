"""
Contains the class that builds and solves the optimization model.
"""
import pulp
from pulp import lpSum
import itertools
import time
from typing import Dict


class OptModel:
    """
    Builds and solves the optimization model.
    """
    def __init__(self, dat_in, model_name: str) -> None:
        """
        Initializes the optimization model and placeholders for future useful data.

        It receives the dat_in parameter, which must be a DatIn instance, containing all the input data properly
        organized to feed the optimization model.

        Parameters
        ----------
        dat_in : DatIn
            A DatIn instance containing the input data (see data_bridge.py).
        model_name : str
            A name for the gurobi model. It cannot contain whitespaces!
        """
        # read input parameters
        self.model_name = model_name
        self.dat_in = dat_in

        # initialize (pulp) optimization model
        self.mdl = pulp.LpProblem(model_name, sense=pulp.LpMinimize)

        # initialize placeholders
        self.sol = None
        self.vars = {}

        # Initialize the Object Function
        self.ObjFunction = pulp.LpAffineExpression()

    def build_base_model(self) -> None:
        """
        Build the base optimization model.
        """
        # Define the model
        print('Building base optimization model...')
        self._add_decision_variables()
        self._add_base_constraints()
        self._build_objective()

    def _add_decision_variables(self) -> None:
        """Add the decision variables."""
        mdl, dat_in = self.mdl, self.dat_in
        x_keys, yp_keys, yg_keys, wb_keys = dat_in.x_keys, dat_in.yp_keys, dat_in.yg_keys, dat_in.wb_keys
        w_keys, xb_keys = dat_in.w_keys, dat_in.xb_keys

        t1 = time.perf_counter()
        # create decision variables

        yp = pulp.LpVariable.dicts(indices=yp_keys, cat=pulp.LpInteger, lowBound=0.0,
                                   name='yp')  # Qty  in Patas Pack
        yg = pulp.LpVariable.dicts(indices=yg_keys, cat=pulp.LpInteger, lowBound=0.0,
                                   name='yg')  # Qty  in Pet Gourmet
        x = pulp.LpVariable.dicts(indices=x_keys, cat=pulp.LpInteger, lowBound=0.0,
                                  name='x')  # Qty of transporting packing
        w = pulp.LpVariable.dicts(indices=w_keys, cat=pulp.LpInteger, lowBound=0.0,
                                  name='w')  # Acquired quantity of packing
        wb = pulp.LpVariable.dicts(indices=wb_keys, cat=pulp.LpBinary,
                                   name='wb')  # Binary decision variable of acquisition
        xb = pulp.LpVariable.dicts(indices=xb_keys, cat=pulp.LpBinary, name='xb')# Binary decision variable of transport

        self.vars['x'] = x
        self.vars['yp'] = yp
        self.vars['yg'] = yg
        self.vars['w'] = w
        self.vars['wb'] = wb
        self.vars['xb'] = xb
        t2 = time.perf_counter()
        print(f"ADDING DECISION VARS: {t2-t1:.4f} s")

    def _add_base_constraints(self) -> None:
        """Add the constraints"""
        mdl, dat_in = self.mdl, self.dat_in
        x, yp, yg = self.vars['x'], self.vars['yp'], self.vars['yg']
        xb, wb, w = self.vars['xb'], self.vars['wb'], self.vars['w']
        
        x_keys, yp_keys, yg_keys, xb_keys = dat_in.x_keys, dat_in.yp_keys, dat_in.yg_keys, dat_in.xb_keys
        w_keys, wb_keys = dat_in.w_keys, dat_in.wb_keys

        I, T= dat_in.I, dat_in.T
        first_period = dat_in.first_period

        d, ilg, ini_inventory, inven_cost = dat_in.d, dat_in.ilg, dat_in.ini_inventory, dat_in.inven_cost
        c, au, moq, params = dat_in.c, dat_in.au, dat_in.moq, dat_in.dat_params

        t00 = time.perf_counter()
        # C1) Inventory capacity:
        for t in T:
            # Patas Pack Inventory Capacity:
            mdl.addConstraint(lpSum(yp[i, t] for i in I) <= params['InventoryCapacityPack'], name=f'C1a_{t}')
            # Pet Gourmet Inventory Capacity:
            mdl.addConstraint(lpSum(yg[i, t] for i in I) <= params['InventoryCapacityGourmet'], name=f'C1b_{t}')

        t1 = time.perf_counter()
        print(f"ADDING C2: {t1 - t00:.4f} s")
        # C2) Minimum and maximum order quantity:
        for i in I:
            for t in T:
                mdl.addConstraint(w[i, t] <= wb[i, t] * au[i, t], name=f'C2a_{t}_{i}')
                mdl.addConstraint(w[i, t] >= wb[i, t] * moq[i, t], name=f'C2b_{t}_{i}')

        t2 = time.perf_counter()
        print(f"ADDING C3: {t2-t1:.4f} s")
        # C3) Transporting limit by period:
        for t in T:
            mdl.addConstraint(lpSum(x[i, t] for i in I) <= params['TransportingLimitByPeriod'], name=f'C3_{t}')

        t3 = time.perf_counter()
        print(f"ADDING C2: {t3-t2:.4f} s")
        # C4) Flow Balance constraint:
        for t in T:
            for i in I:
                mdl.addConstraint(yg[i, t] == yg[i, t - 1] + x[i, t] - d[i, t], name=f'C4a_{t}_{i}')
                mdl.addConstraint(yp[i, t] == yp[i, t - 1] + w[i, t] - x[i, t], name=f'C4b_{t}_{i}')
        
        t4 = time.perf_counter()
        print(f"ADDING C3: {t4-t3:.4f} s")
        # C5) Minimum Inventory constraint:
        for t in T:
            for i in I:
                mdl.addConstraint(yg[i, t] >= ilg['Gourmet', i], name=f'C5_{t}_{i}')

        t5 = time.perf_counter()
        print(f"ADDING C4: {t5-t4:.4f} s")
        # C6) Maximum time in Patas Pack constraint:
        for t in T:
            if t <= max(T) - params['MaxTimePackingPack']:
                for i in I:
                    mdl.addConstraint(
                        lpSum(x[i, t + l] for l in range(1, int(params['MaxTimePackingPack']) + 1)) >= yp[i, t],
                        name=f'C6_{t}_{i}')

        t6 = time.perf_counter()
        print(f"ADDING C5: {t6-t5:.4f} s")
        # C7) Initial Inventory Constraint:
        for i in I:
            mdl.addConstraint(yp[i, first_period - 1] == ini_inventory['Pack', i], name=f'C7a_{i}')
            mdl.addConstraint(yg[i, first_period - 1] == ini_inventory['Gourmet', i], name=f'C7b_{i}')
        
        t6 = time.perf_counter()
        print(f"ADDING C6: {t6-t5:.4f} s")
        # C8) Maximum number of different packing types that can be transferred:
        for t in T:
            mdl.addConstraint(lpSum(xb[i, t] for i in I) <= params['DiversityTransportingPacking'])

        t7 = time.perf_counter()
        print(f"ADDING C7: {t7-t6:.4f} s")
        # C9) Maximum transfer quantity for each packing:
        for i in I:
            for t in T:
                mdl.addConstraint(x[i, t] <= xb[i, t] * params['TransportingLimitByPeriod'])

        t8 = time.perf_counter()
        print(f"ADDING C9: {t8-t7:.4f} s")



    def _build_objective(self) -> None:
        """
        Build and set the objective function.
        """
        mdl, dat_in = self.mdl, self.dat_in
        I = dat_in.I
        T = dat_in.T
        x, yp, yg, w = self.vars['x'], self.vars['yp'], self.vars['yg'], self.vars['w']
        c, inven_cost = dat_in.c, dat_in.inven_cost

        # Trocar os conjuntos pelas keys deixa o código mais ROBUSTO!
        # Objective function

        self.ObjFunction += lpSum(c[i] * w[i, t] for i in I for t in T) +\
        lpSum(inven_cost['Pack', i] * yp[i, t] for i in I for t in T) +\
        lpSum(inven_cost['Gourmet', i] * yg[i, t] for i in I for t in T)

        # mdl.setObjective(
        #    lpSum(c[i] * w[i, t] for i in I for t in T) +
        #    lpSum(inven_cost['Pack', i] * yp[i, t] for i in I for t in T) +
        #    lpSum(inven_cost['Gourmet', i] * yg[i, t] for i in I for t in T)
        # )

    def transporting_cost_complexity(self):
        mdl, dat_in = self.mdl, self.dat_in
        x = self.vars['x']
        I, T = dat_in.I, dat_in.T
        n_keys = [t for t in T]
        params = dat_in.dat_params

        # New Variable due the complexity
        n = pulp.LpVariable.dicts(indices=n_keys, cat=pulp.LpInteger, lowBound=0.0,
                                  name='n')  # Qty of trucks

        # New constraints
        mdl.addConstraint((n[t] >= lpSum(x[i, t]/params['TransportingLimitByPeriod'] for i in I), for t in T),
                          name=f'newC1')

        mdl.addConstraint((n[t] <= lpSum(x[i, t] / params['TransportingLimitByPeriod']  for i in I) + 1, for t in T),
                          name=f'newC1')

        # Update of the Objective Function
        self.ObjFunction += n*350

        return

    def discount_complexity(self):
        mdl, dat_in = self.mdl, self.dat_in
        w = self.vars['w']
        c = dat_in.c
        I, T = dat_in.I, dat_in.T
        dc_keys = [(i, t) for i in I for t in T]
        params = dat_in.dat_params

        # New variable due the complexity
        dc = pulp.LpVariable.dicts(indices=dc_keys, cat=pulp.LpBinary, name='dc')

        # New constraints
        for i in I:
            for t in T:
                mdl.addConstraint(dc[i, t]*w[i, t] >= w[i, t] - params['DiscountLimit'], name=f'disC1a_{i}_{t}')
                mdl.addConstraint(dc[i, t]*(w[i, t] - params['DiscountLimit']) >= w[i,t] - params['DiscountLimit'],
                                  name=f'discC1b_{i}_{t}')

        self.ObjFunction += lpSum(-0.10*c[i]*w[i, t] for i in I for t in T)

    def set_model_parameters(self, parameters: Dict[str, float]) -> None:
        """
        Set parameters to the gurobi model.

        Some common parameters are "TimeLimit" and "MIPGap".

        Parameters
        ----------
        parameters : dict
            Dictionary whose keys are names of gurobi model's parameters (str) and whose values are values for these
            parameters.
        """
        # Para o Pulp isso será diferente:
        # for param, value in parameters.items():
        #     setattr(self.mdl.params, param, value)

    def optimize(self) -> None:
        """
        Calls the optimizer, and populates the solution data (if any).
        """
        print('Solving the optimization model...')
        mdl = self.mdl
        mdl.setObjective(self.ObjFunction)
        mdl.solve()

        # print status
        status = mdl.status
        status_str = pulp.LpStatus[status]

        print(f"Model status: {status_str}")

        # build solution
        if status == pulp.LpStatusOptimal:

            x, w = self.vars['x'], self.vars['w']
            yp, yg, wb, xb = self.vars['yp'], self.vars['yg'], self.vars['wb'], self.vars['xb']
            x_sol = [(i, t, var.value()) for (i, t), var in x.items()]
            yp_sol = [(i, t, var.value()) for (i, t), var in yp.items()]
            yg_sol = [(i, t, var.value()) for (i, t), var in yg.items()]
            w_sol = [(i, t, var.value()) for (i, t), var in w.items()]
            wb_sol = [(i, t, var.value()) for (i, t), var in wb.items()]  # without future use

            # kpis_sol = [
            #     ('Total Cost', self.total_cost.getValue()),
            #     ('Total Procurement Cost', self.purchase_cost.getValue()),
            #     ('Total Inventory Holding Cost (supplier)', self.inventory_cost_s.getValue()),
            #     ('Total Inventory Holding Cost (warehouse)', self.inventory_cost.getValue()),
            # ]

            self.sol = {
                'status': status,
                'obj_val': self.mdl.objective.value(),
                'vars': {'x': x_sol, 'yp': yp_sol, 'yg': yg_sol, 'w': w_sol}
            }

        else:
            self.sol = {'status': status}
