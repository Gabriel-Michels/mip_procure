import itertools
import pandas as pd
from mip_procure.schemas import input_schema, output_schema
from mip_procure.utils import BadSolutionError, is_list_of_consecutive_increasing_integers
import pulp
from mip_procure.data_preparation import all_integrity_checks

class DatIn:
    """
    Class that prepares the data (from the input tables, stored in a PanDat object) to be consumed by the main engine.

    Every set and every parameter defined in the mathematical formulation is populated here from the input
    tables and set as an attribute of this class. As a result, the optimization model becomes identical
    to the mathematical formulation, which facilitates debugging and maintenance.
    """

    def __init__(self, dat: input_schema.PanDat, verbose: bool = False) -> None:
        """
        Initializes a DatIn instance, from a dat object.

        When a DatIn instance is initialized (i.e., when this method is called), we read the input data (tables as
        pandas dataframes, stored in the dat parameter) and populate all the optimization indices/parameters as
        instance attributes.

        Parameters
        ----------
        dat : input_schema.PanDat
            A PanDat object from ticdat package, created accordingly to schemas.input_schema. It contains the input 
            data as its attributes (pandas dataframes).
        """
        print('Instantiating a DatIn object...')
        self.dat = input_schema.copy_pan_dat(pan_dat=dat)  # copy input "dat" to avoid over-writing
        self.dat_params = input_schema.create_full_parameters_dict(dat)  # create input parameters from 'dat'

        # Additional integrity checks
        all_integrity_checks(self.dat)

        # set of indices, populated in _populate_sets_of_indices() method
        self.I = set()  # set of items ids
        self.J = set()  # set of facilities
        self.T = set()  # set of time periods
        self.T_extend = set() # set of extended time periods (I think it's not necessary)

        # parameters, populated in _populate_parameters() method
        self.first_period = None  # int, first time period
        self.d = {}  # dict {(i,t) : demand at period t}
        self.ilg = {}  # dict {(j, i) :lower bound of packing i inventory of factory j}
        self.ini_inventory = {}  # dict {(j, i) initial inventory of packing i of factory j}
        self.inven_cost = {}
        self.c = {}  # dict {i: Unit Price of packing i}
        self.au = {}  # dict {
        self. moq = {}  # dict { (i, t): Minimum order quantity of packing i at period t}
        self.params = {} # input schema parametres.

        # auxiliary data
        self.suppliers_ids = set()  # set of suppliers ids. For my case it's not necessary
        self.warehouses_ids = set()  # set of warehouses ids. For my case it's not necessary
        self.x_keys = []
        self.yp_keys = []
        self.yg_keys = []
        self.w_keys = []
        self.wb_keys = []
        self.xb_keys = []

        # populate optimization data. The order below in which methods are called is important! Don't change it!
        print("Populating the optimization data...")
        self._populate_sets_of_indices()
        self._populate_parameters()
        self._derive_variables_keys()

        if verbose:
            self.print_opt_data()

    def _populate_sets_of_indices(self) -> None:
        """
        Populates the set of indices I, T, and K, used to add constraints to the optimization model.
        """
        dat = self.dat
        self.I = set(dat.packing['Packing ID'])
        self.J = set(dat.inventory['Factory ID'])
        self.T = set(dat.demand_packing['Period ID'])
        self.first_period = min(self.T)
        self.T_extend = self.T.union({self.first_period - 1})
    
    def _populate_parameters(self) -> None:
        """
        Populate the parameters to be used when adding constraints and the objective function to the
        optimization model.
        """
        dat = self.dat

        # filter some input tables by splitting their data into Suppliers and Warehouses
        # inventory_df_suppliers = dat.inventory[dat.inventory['Site ID'].isin(self.suppliers_ids)]
        # inventory_df_warehouses = dat.inventory[dat.inventory['Site ID'].isin(self.warehouses_ids)]

        self.first_period = min(self.T)
        self.params = input_schema.create_full_parameters_dict(dat)
        self.d = dict(zip(zip(dat.demand_packing['Packing ID'], dat.demand_packing['Period ID']),
                     dat.demand_packing['Demand']))
        self.ilg = dict(zip(zip(dat.inventory['Factory ID'], dat.inventory['Packing ID']),
                       dat.inventory['Minimum Inventory']))
        self.ini_inventory = dict(zip(zip(dat.inventory['Factory ID'], dat.inventory['Packing ID']),
                                 dat.inventory['Initial Inventory']))
        self.c = dict(zip(dat.packing['Packing ID'], dat.packing['Unit Price']))
        self.inven_cost = dict(zip(zip(dat.inventory['Factory ID'], dat.inventory['Packing ID']),
                              dat.inventory['Inventory Cost']))
        self.au = dict(zip(zip(dat.demand_packing['Packing ID'], dat.demand_packing['Period ID']),
                      dat.demand_packing['Max Order Qty']))
        self.moq = dict(zip(zip(dat.demand_packing['Packing ID'], dat.demand_packing['Period ID']),
                       dat.demand_packing['Min Order Qty']))

    def _derive_variables_keys(self) -> None:

        I, T = self.I, self.T
        self.first_period = min(self.T)
        self.T_extend = self.T.union({self.first_period - 1})
        T_extend = self.T_extend

        self.x_keys = [(i, t) for i in I for t in T]
        self.w_keys = self.x_keys.copy()
        self.wb_keys = self.x_keys.copy()
        self.xb_keys = self.x_keys.copy()
        self.yp_keys = [(i, t) for i in I for t in T_extend]
        self.yg_keys = self.yp_keys.copy()
        
    def print_opt_data(self) -> None:
        """
        Prints the indices/parameters created for the optimization engine.
        """
        for attr_name, value in self.__dict__.items():
            if attr_name.startswith('_'):
                continue
            print(f"{attr_name}:")
            print(value)
            print('-' * 40)


class DatOut:
    """
    Processes the output from the main engine and populates the output tables, stored as pandas dataframes
    (attributes of DatOut instances).

    The user can get a PanDat object containing the output dataframes by calling the build_output() method (which
    retrieves a PanDat), and/or print them through print_solution_dataframes() method.
    """

    def __init__(self, solution_model) -> None:
        """
        Initializes a DatOut instance from the solved optimization model, and populates the output tables.

        Parameters
        ----------
        solution_model : OptModel
            An instance of the OptModel class (see opt_model.py) which has already called its optimize() method. It
            contains   output data from optimization to feed the DatOut class.
        """
        print('Instantiating a DatOut object...')
        # get optimal data
        self.solution_model = solution_model
        self.opt_sol = solution_model.sol
        self.dat_in: DatIn = solution_model.dat_in

        # initialize output data
        self.patas_pack_df = None
        self.pet_gourmet_df = None

        # populate the solution dataframes
        self._process_solution()

    def _process_solution(self) -> None:
        """
        Converts the output from the optimization into dataframes that will be used to build reports.
        """
        dat_in, dat = self.dat_in, self.dat_in.dat
        # I, T = dat_in.I, dat_in.T
        mdl = self.solution_model.mdl
        # print status
        status = mdl.status
        status_str = pulp.LpStatus[status]

        if status != pulp.LpStatusOptimal:
            return
        
        # read output variables values from optimization
        vars_sol = self.opt_sol['vars']
        x_sol = vars_sol['x']
        yp_sol = vars_sol['yp']
        yg_sol = vars_sol['yg']
        w_sol = vars_sol['w']

        # create the output dataframe
        x_df = pd.DataFrame(data=x_sol, columns=['Packing ID', 'Period ID', 'Transferred Quantity'])
        w_df = pd.DataFrame(w_sol, columns=['Packing ID', 'Period ID', 'Acquired Quantity'])
        yp_df = pd.DataFrame(yp_sol, columns=['Packing ID', 'Period ID', 'Final Inventory'])
        yg_df = pd.DataFrame(yg_sol, columns=['Packing ID', 'Period ID', 'Final Inventory'])

        # demand table
        demand_packing_df = dat.demand_packing.copy()
        demand_df = demand_packing_df[['Packing ID', 'Period ID', 'Demand']]

        # Pet Gourmet Table
        pet_gourmet_df = x_df.merge(yg_df, on=['Packing ID', 'Period ID'], how='left')
        pet_gourmet_df = demand_df.merge(pet_gourmet_df, on=['Packing ID', 'Period ID'], how='right')
        # if demand wasn't specified then we don't have demand.
        pet_gourmet_df['Demand'] = pet_gourmet_df['Demand'].fillna(0)
        pet_gourmet_df['Initial Inventory'] = (pet_gourmet_df['Demand'] + pet_gourmet_df['Final Inventory']
                                               - pet_gourmet_df['Transferred Quantity'])
        new_order = ['Packing ID', 'Period ID', 'Initial Inventory', 'Demand',
                     'Transferred Quantity', 'Final Inventory']
        pet_gourmet_df = pet_gourmet_df[new_order]
        pet_gourmet_df = pet_gourmet_df.sort_values(by=['Packing ID', 'Period ID'],
                                                    ascending=[True, True], ignore_index=True)
        self.pet_gourmet_df = pet_gourmet_df

        # Patas Pack table
        patas_pack_df = x_df.merge(yp_df, on=['Packing ID', 'Period ID'], how='left')
        patas_pack_df = patas_pack_df.merge(w_df, on=['Packing ID', 'Period ID'], how='left')
        # y[i, t] == y[i, t - 1] + w[i, t] - x[i, t] remember the flow balance's equation
        patas_pack_df['Initial Inventory'] = (patas_pack_df['Transferred Quantity'] +
                                              patas_pack_df['Final Inventory'] - patas_pack_df['Acquired Quantity'])
        new_order = ['Packing ID', 'Period ID', 'Initial Inventory', 'Transferred Quantity',
                     'Acquired Quantity', 'Final Inventory']
        patas_pack_df = patas_pack_df[new_order]
        patas_pack_df = patas_pack_df.sort_values(by=['Packing ID', 'Period ID'],
                                                  ascending=[True, True], ignore_index=True)
        self.patas_pack_df = patas_pack_df

    def build_output(self) -> output_schema.PanDat:
        """
        Populates the output "sln" object.

        Returns
        -------
        sln : output_schema.PanDat
            A PanDat object from ticdat package, accordingly to the schemas.output_schema, that contains all output
            tables as attributes.
        """
        print('Building output dat...')
        sln = output_schema.PanDat()
        sln.pet_gourmet = self.pet_gourmet_df
        sln.patas_pack = self.patas_pack_df

        return sln
