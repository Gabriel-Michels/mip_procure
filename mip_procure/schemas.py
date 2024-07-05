from ticdat import PanDatFactory

# region INPUT SCHEMA
input_schema = PanDatFactory(
   parameters=[['Name'], ['Value']], # No change the column's name
   packing=[['Packing ID'], ['Unit Price', 'Size', 'Color']],
   demand_packing=[['Packing ID', 'Period ID'], ['Demand', 'Min Order Qty', 'Max Order Qty']],
   inventory=[['Factory ID', 'Packing ID'], ['Initial Inventory', 'Minimum Inventory', 'Inventory Cost']],
   distribution=[['Packing ID'], ['Minimum Transfer Qty', 'Maximum Transfer Qty']],
   items_aging=[['Packing ID'], ['Maximum Time']])
# endregion

# region Foreign keys
input_schema.add_foreign_key(native_table='demand_packing', foreign_table='packing',
                             mappings=[('Packing ID', 'Packing ID')])
input_schema.add_foreign_key(native_table='distribution',  foreign_table='packing',
                             mappings=[('Packing ID', 'Packing ID')])
input_schema.add_foreign_key(native_table='items_aging', foreign_table='packing',
                             mappings=[('Packing ID', 'Packing ID')])
# endregion

# region DATA TYPES
# region packing
input_schema.set_data_type(table = 'packing', field='Packing ID', number_allowed=False, strings_allowed='*')
input_schema.set_data_type(table = 'packing', field='Unit Price', number_allowed=True,
                           strings_allowed=(), must_be_int=False)
input_schema.set_data_type(table='packing', field='Color', number_allowed=False, strings_allowed='*')
input_schema.set_data_type(table='packing', field='Size', number_allowed=True, strings_allowed=(), must_be_int=True)
input_schema.set_default_value(table='packing', field='Unit Price', default_value=0.20)
# endregion

# region demand_packing
input_schema.set_data_type(table = 'demand_packing', field='Packing ID', number_allowed=False, strings_allowed='*')
input_schema.set_data_type(table = 'demand_packing', field='Demand', number_allowed=True, strings_allowed=())
input_schema.set_data_type(table = 'demand_packing', field='Period ID', number_allowed=True, strings_allowed=())
input_schema.set_data_type(table = 'demand_packing', field='Max Order Qty',
                           number_allowed=True, strings_allowed=())
input_schema.set_data_type(table = 'demand_packing', field='Min Order Qty',
                           number_allowed=True, strings_allowed=())
# endregion

# region inventory
input_schema.set_data_type(table='inventory', field='Factory ID', number_allowed=False,
                           strings_allowed=('Pack', 'Gourmet'))
input_schema.set_data_type(table='inventory', field='Packing ID', number_allowed=False, strings_allowed='*')
input_schema.set_data_type(table='inventory', field='Initial Inventory', number_allowed=True, strings_allowed=(),
                            min=0.0, inclusive_min=True, max=float('inf'), inclusive_max=False)
input_schema.set_data_type(table='inventory', field='Minimum Inventory', number_allowed=True, strings_allowed=(),
                            min=0.0, inclusive_min=True, max=float('inf'), inclusive_max=False)

input_schema.set_data_type(table='inventory', field='Inventory Cost', number_allowed=True, strings_allowed=(),
                            min=0.0, inclusive_min=True, max=float('inf'), inclusive_max=False)
# endregion

# region items aging
input_schema.set_data_type(table='items_aging', field='Packing ID', number_allowed=False, strings_allowed='*')
input_schema.set_data_type(table='items_aging', field='Maximum Time', number_allowed=True, strings_allowed=())
# endregion

# region distribution
input_schema.set_data_type(table = 'distribution', field='Packing ID', number_allowed=False, strings_allowed='*')
input_schema.set_data_type(table='distribution', field='Minimum Transfer Qty', number_allowed=True, min=0,
                           inclusive_min=True, must_be_int=True, strings_allowed=())
input_schema.set_data_type(table='distribution', field='Maximum Transfer Qty', number_allowed=True, must_be_int=True,
                           min=0, inclusive_min=True, strings_allowed=())
# endregion
# endregion

# region Parameters
input_schema.add_parameter('Packing Cost Multiplier', default_value=1.2, number_allowed=True, strings_allowed=(),
                           must_be_int=False, min=0.0, inclusive_min=True, max=10, inclusive_max=True)
input_schema.add_parameter('InventoryCapacityPack', default_value=5000, number_allowed=True,
                           strings_allowed=(), min=0.0, inclusive_min=True)
input_schema.add_parameter('InventoryCapacityGourmet', default_value=4000, number_allowed=True,
                           strings_allowed=(), min=0.0, inclusive_min=True)
input_schema.add_parameter('TransportingLimitByPeriod', default_value=40000, number_allowed=True,
                           strings_allowed=(), min=0.0, inclusive_min=True)
input_schema.add_parameter('MaxTimePackingPack', default_value=1, number_allowed=True,
                           strings_allowed=(), min=1, inclusive_min=True, must_be_int=True)
input_schema.add_parameter('DiversityTransportingPacking', default_value=5, number_allowed=True,
                           strings_allowed=(), min=1, inclusive_min=True, must_be_int=True)
# endregion

# region predicate
input_schema.add_data_row_predicate(table='distribution', predicate_name='Minimum Transfer Qty <= Maximum Transfer Qty',
                                    predicate=lambda row: row['Minimum Transfer Qty'] <= row['Maximum Transfer Qty'])
# endregion

# region OUTPUT SCHEMA
output_schema = PanDatFactory(
    pet_gourmet=[['Packing ID', 'Period ID'], ['Initial Inventory',  'Demand',
                                               'Transferred Quantity', 'Final Inventory']],
    patas_pack=[['Packing ID', 'Period ID'], ['Initial Inventory', 'Transferred Quantity',
                                              'Acquired Quantity', 'Final Inventory']]
)
# endregion

# region data types - OUTPUT SCHEMA
# region pet_gourmet
table = 'pet_gourmet'
output_schema.set_data_type(table=table, field='Packing ID', number_allowed=False,
                            strings_allowed=('P1', 'P2', 'P3', 'P4', 'P5', 'P6'))
output_schema.set_data_type(table=table, field='Period ID', number_allowed=True, must_be_int=True, strings_allowed=())
output_schema.set_data_type(table=table, field='Initial Inventory', strings_allowed=(), min=0, inclusive_min=True,
                            max=float('inf'), inclusive_max=False)
output_schema.set_data_type(table=table, field='Demand',  strings_allowed=(),
                            min=0, inclusive_min=True, max=float('inf'), inclusive_max=False)
output_schema.set_data_type(table=table, field='Transferred Quantity',  strings_allowed=(),
                            min=0, inclusive_min=True, max=float('inf'), inclusive_max=False)
output_schema.set_data_type(table=table, field='Final Inventory',  strings_allowed=(),
                            min=0, inclusive_min=True, max=float('inf'), inclusive_max=False)
# endregion

#region patas_pack
table = 'patas_pack'
output_schema.set_data_type(table=table, field='Packing ID', number_allowed=False,
                            strings_allowed=('P1', 'P2', 'P3', 'P4', 'P5', 'P6'))
output_schema.set_data_type(table=table, field='Period ID', number_allowed=True, must_be_int=True, strings_allowed=())
output_schema.set_data_type(table=table, field='Initial Inventory', strings_allowed=(), min=0, inclusive_min=True,
                            max=float('inf'), inclusive_max=False)
output_schema.set_data_type(table=table, field='Acquired Quantity',  strings_allowed=(),
                            min=0, inclusive_min=True, max=float('inf'), inclusive_max=False)
output_schema.set_data_type(table=table, field='Final Inventory',  strings_allowed=(),
                            min=0, inclusive_min=True, max=float('inf'), inclusive_max=False)
# endregion
# endregion
