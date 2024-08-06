from test_mip_procure import utils
from pathlib import Path
import pandas as pd
import mip_procure
import unittest

pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 4000)

cwd = Path(__file__).parent.resolve()


class TestLocalExecution(unittest.TestCase):
    """
    THIS IS NOT UNIT TESTING! Unit testing are implemented in other scripts.

    This class only serves the purpose of conveniently (with one click) executing solve engines locally during
    development.

    In addition, the methods in this class mimic the execution flow that a user typically experience on a Mip Hub app.
    """

    def test_1_action_data_ingestion(self):
        dat = utils.read_data(input_data_loc=f"{cwd}/data/testing_data/validation_data.xlsx", schema=mip_procure.input_schema)
        utils.check_data(dat, mip_procure.input_schema)
        utils.write_data(dat, f'{cwd}/data/inputs', mip_procure.input_schema)

    # testing_data / mip_procure_input_data_v1.xlsx
    def test_2_main_solve(self):
        dat = utils.read_data(f'{cwd}/data/inputs', mip_procure.input_schema)
        sln = mip_procure.solve(dat)
        utils.write_data(sln, f'{cwd}/data/outputs', mip_procure.output_schema)