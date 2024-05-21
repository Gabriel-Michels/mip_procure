from ticdat import PanDatFactory



# region INPUT SCHEMA
input_schema = PanDatFactory(
   parameters=[['Parameter'], ['Value']],
   packing=[['Packing ID'], ['Unit Price', 'Size', 'Color']],
   #periods=[["Period ID"], ['Start Date', 'End Date']], #I forgot the reason of this table
   demand_packing=[['Packing ID', 'Period ID'], ['Demand']],  #Proposed solution by Luiz (The GOAT)
   inventory=[['Factory ID', 'Packing ID'], ['Initial Inventory', 'Minimum Inventory' 'Inventory Cost']],
   distribution=[['Packing ID'], ['Minimum Transfer Qty', 'Maximum Transfer Qty', 'Lead Time']]
   items_aging=[['Packing ID'], ['Maximum Time',]] #Luiz thinks that this can be a parameter.
)
# endregion

#Region Foreign keys

input_schema.add_foreign_key(native_table='demand_packing', foreign_table='packing', mappings=[('Packing ID', 'Packing ID')])
input_schema.add_foreign_key(native_table='distribution',  foreign_table='packing', mappings=[('Packing ID', 'Packing ID')])
input_schema.add_foreign_key(native_table='items_aging', foreign_table='packing', mappings=[('Packing ID', 'Packing ID')])




#region DATA TYPES
#I have made just some examples in order to get more practice.
#region packing
input_schema.set_data_type(table = 'packing', field='Packing ID', number_allowed=True, strings_allowed='', must_be_int=True)
input_schema.set_data_type(table = 'packing', field='Unit Price', number_allowed=True, strings_allowed='', must_be_int=False)
input_schema.set_data_type(table='packing', field='Color', number_allowed=False, strings_allowed='*')
input_schema.set_data_type(table='packing', field='Size', number_allowed=True, strings_allowed='', must_be_integer=True)
input_schema.set_default_value(table='packing', field='Unit Price', default_value=0.20)
#end of region

#region demandpacking
input_schema.set_data_type(table = 'demand_packing', field='Packing ID', number_allowed=True, strings_allowed='', must_be_int=True)
input_schema.set_data_type(table = 'demand_packing', field='Demand', number_allowed=True, strings_allowed='')
input_schema.set_data_type(table = 'demand_packing', field='Period ID', number_allowed=True, strings_allowed='')
input_schema.set_data_type(table = 'demand_packing', field='Week2 demand', number_allowed=True, strings_allowed='')
#endregion



#table = 'storage'
#for field in ['Factory ID', 'Storage Capacity', 'Storage Cost']:
 #   input_schema.set_data_type(table=table, field=field, number_allowed=True, strings_allowed='')

#region distribution
#table='distribution'
#for field in ['Packing ID','Minimum', 'Maximum', 'Time transportation']:
 #  input_schema.set_data_type(table=table, field=field, numbel_allowed=True, strings_allowed='')

#input_schema.add_data_row_predicate(table = 'distribution', predicate_name='Minimum <= Maximum',
                                   # predicate=lambda row: row['Minimum'] <= row['Maximum'])
#endregion


#region packing_in_pataspack
#table='packing_in_pataspack'
#for field in ['Packing ID', 'Maximum time in days']:
 #  input_schema.set_data_type(table=table, field=field, numbel_allowed=True, strings_allowed='', must_be_integer=True)
#endregion

#for field in ['Factory Id', 'Initial inventory Patas Pack', 'Initial inventory Pet Gourmet']:
 #  input_schema.set_data_type(table=table, field=field, numbel_allowed=True, strings_allowed='')



#Output Schema.








