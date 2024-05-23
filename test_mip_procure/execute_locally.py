from mip_procure import input_schema
path = 'data/inputs'
dat = input_schema.csv.create_pan_dat(path)
print(dat)