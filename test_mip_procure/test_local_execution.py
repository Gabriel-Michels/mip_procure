from pathlib import Path
import pandas as pd
from mip_procure import input_schema, output_schema
from mip_procure import solve

pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 4000)

cwd = Path(__file__).parent.resolve()

# Read input data
input_path = cwd / 'data/inputs'
dat = input_schema.csv.create_pan_dat(input_path)

# Check input data
data_type_failures = input_schema.find_data_type_failures(dat)
print('data_type_failures:\n', data_type_failures)
foreign_failures = input_schema.find_foreign_key_failures(dat)
print('foreign_failures:\n', foreign_failures)
duplicates = input_schema.find_duplicates(dat)
print('duplicates:\n', duplicates)
row_failures = input_schema.find_data_row_failures(dat)
print('row_failures:', row_failures)

# optimize
sln = solve(dat)

# Check output data
print('\nCheck output data:\n')
data_type_failures = output_schema.find_data_type_failures(sln)
print('data_type_failures:\n', data_type_failures)
foreign_failures = output_schema.find_foreign_key_failures(sln)
print('foreign_failures:\n', foreign_failures)
duplicates = output_schema.find_duplicates(sln)
print('duplicates:\n', duplicates)
row_failures = output_schema.find_data_row_failures(sln)
print('row_failures:', row_failures)

# Write output data
output_path = cwd / 'data/outputs/'
output_schema.csv.write_directory(sln, output_path)
output_schema.xls.write_file(sln, output_path / 'Output.xlsx')
