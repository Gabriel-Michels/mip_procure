from ticdat import PanDatFactory



# region INPUT SCHEMA
input_schema = PanDatFactory(
   parameters=[['Name'], ['Value']], #No change the column's name
   packing=[['Packing ID'], ['Unit Price', 'Size', 'Color']],
   #periods=[["Period ID"], ['Start Date', 'End Date']], #I forgot the reason of this table
   demand_packing=[['Packing ID', 'Period ID'], ['Demand', 'Acquisition Limit Period', 'Transport Limit Period']],  #Proposed solution by Luiz (The GOAT)
   inventory=[['Factory ID', 'Packing ID'], ['Initial Inventory', 'Minimum Inventory', 'Inventory Cost']],
   distribution=[['Packing ID'], ['Minimum Transfer Qty', 'Maximum Transfer Qty', 'Lead Time']],
   items_aging=[['Packing ID'], ['Maximum Time']]) #Luiz thinks that this can be a parameter.

# endregion

#Region Foreign keys

input_schema.add_foreign_key(native_table='demand_packing', foreign_table='packing', mappings=[('Packing ID', 'Packing ID')])
input_schema.add_foreign_key(native_table='distribution',  foreign_table='packing', mappings=[('Packing ID', 'Packing ID')])
input_schema.add_foreign_key(native_table='items_aging', foreign_table='packing', mappings=[('Packing ID', 'Packing ID')])




#region DATA TYPES
#I have made just some examples in order to get more practice.
#region packing
input_schema.set_data_type(table = 'packing', field='Packing ID', number_allowed=False, strings_allowed='*')
input_schema.set_data_type(table = 'packing', field='Unit Price', number_allowed=True, strings_allowed=(), must_be_int=False)
input_schema.set_data_type(table='packing', field='Color', number_allowed=False, strings_allowed='*')
input_schema.set_data_type(table='packing', field='Size', number_allowed=True, strings_allowed=(), must_be_int=True)
input_schema.set_default_value(table='packing', field='Unit Price', default_value=0.20)
#end of region

#region demandpacking
input_schema.set_data_type(table = 'demand_packing', field='Packing ID', number_allowed=False, strings_allowed='*')
input_schema.set_data_type(table = 'demand_packing', field='Demand', number_allowed=True, strings_allowed=())
input_schema.set_data_type(table = 'demand_packing', field='Period ID', number_allowed=True, strings_allowed=())
#endregion

#region inventory

input_schema.set_data_type(table='inventory', field='Factory ID', number_allowed=False, strings_allowed=('Pack', 'Gourmet'))
input_schema.set_data_type(table='inventory', field='Packing ID', number_allowed=False, strings_allowed='*')
input_schema.set_data_type(table='inventory', field='Initial Inventory', number_allowed=True, strings_allowed=(),
                            min=0.0, inclusive_min=True, max=float('inf'), inclusive_max=False)
input_schema.set_data_type(table='inventory', field='Minimum Inventory', number_allowed=True, strings_allowed=(),
                            min=0.0, inclusive_min=True, max=float('inf'), inclusive_max=False)

input_schema.set_data_type(table='inventory', field='Inventory Cost', number_allowed=True, strings_allowed=(),
                            min=0.0, inclusive_min=True, max=float('inf'), inclusive_max=False)

#Parameters

input_schema.add_parameter('Packing Cost Multiplier', default_value=1.2, number_allowed=True, strings_allowed=(),
                           must_be_int=False, min=0.0, inclusive_min=True, max=10, inclusive_max=True)
input_schema.add_parameter('InventoryCapacityPack', default_value=5000, number_allowed=True, strings_allowed=(), min=0.0, inclusive_min=True)
input_schema.add_parameter('InventoryCapacityGourmet', default_value=4000, number_allowed=True, strings_allowed=(), min=0.0, inclusive_min=True)
input_schema.add_parameter('TransportingLimitByPeriod', default_value=4000, number_allowed=True, strings_allowed=(), min=0.0, inclusive_min=True)
input_schema.add_parameter('MaxTimePackingPack', default_value=1, number_allowed=True, strings_allowed=(), min=1, inclusive_min=True, must_be_int=True)
input_schema.add_parameter('AcquisitionLimitPeriod', default_value=4000, number_allowed=True, strings_allowed=(), min=0, inclusive_min=True, must_be_int=True)




#endregion


distribution=[['Packing ID'], ['Minimum Transfer Qty', 'Maximum Transfer Qty', 'Lead Time']],

#predicateregion
input_schema.add_data_row_predicate(table='distribution', predicate_name='Minimum Transfer Qty <= Maximum Transfer Qty',
                                    predicate=lambda row: row['Minimum Transfer Qty'] <= row['Maximum Transfer Qty'])
#endregion

# region OUTPUT SCHEMA
output_schema = PanDatFactory(
    acquisition_by_period=[['Packing ID', 'Period ID'], ['Acquired Quantity', 'Transferred Quantity']],
    pet_gourmet=[['Packing ID', 'Period ID'], ['Initial Inventory',  'Demand', 'Final Inventory']],
    patas_pack=[['Packing ID', 'Period ID'], ['Initial Inventory', 'Transferred Quantity', 'Final Inventory']]
)





table = 'acquisition_by_period'
output_schema.set_data_type(table=table, field='Packing ID', number_allowed=False, strings_allowed='*')
output_schema.set_data_type(table=table, field='Period ID', number_allowed=True, strings_allowed=())
output_schema.set_data_type(table=table, field='Acquired Quantity', number_allowed=True, strings_allowed=())



# endregion













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








