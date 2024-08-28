from mip_procure.data_bridge import DatIn, DatOut
from mip_procure.opt_model import OptModel
from mip_procure.schemas import input_schema, output_schema


def solve(dat: input_schema.PanDat) -> output_schema.PanDat:
    dat_in = DatIn(dat, verbose=True)
    opt_model = OptModel(dat_in, model_name='Mip_Procure')
    opt_model.build_base_model()
    opt_model.transporting_cost_complexity()
    opt_model.optimize()
    opt_model.mdl.writeLP('lp.lp') # It is very useful in infeasible solutions debug.
    dat_out = DatOut(opt_model)
    sln = dat_out.build_output()
    return sln