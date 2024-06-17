__version__ = "0.1.0"
from mip_procure.main import solve
from mip_procure.schemas import input_schema, output_schema
from mip_procure.action_update_packing_cost import update_packing_cost_solve
# from mip_me.action_report_builder import report_builder_solve (I don't know anything about this)

actions_config = {
    'Update Packing Cost': {
        'schema': 'input',
        'engine': update_packing_cost_solve,
        'tooltip': "Update the packing cost by the factor entered in the 'Packing Cost Multiplier' parameter"},
    }

parameters_config = {
    'hidden': list(),
    'categories': dict(),
    'order': ['AcquisitionLimitPeriod', 'MaxTimePackingPack', 'TransportingLimitByPeriod',
              'InventoryCapacityGourmet', 'InventoryCapacityPack', 'Packing Cost Multiplier'],
    'tooltips': {
        'AcquisitionLimitPeriod': 'The limit of Acquisition of packing in a period',
        'MaxTimePackingPack': 'The limit time of a packing stored in Patas Pack',
        'TransportingLimitByPeriod': 'The maximum of packing that can be transported from Patas Pack to Pet Gourmet',
        'InventoryCapacityGourmet': 'The maximum quantity of packing in Pet Gourmet',
        'InventoryCapacityPack': 'The maximum quantity of packing in Patas Pack',
        'Packing Cost Multiplier': 'The factor that can be used by the Update Packing Cost'
        }
    }

# input_tables_config:
input_tables_config = {
    'hidden_tables': ['parameters'],
    'categories': dict(),
    'order': list(),
    'tables_display_names': dict(),
    'columns_display_names': dict(),
    'hidden_columns': {'packing': ['Color']
                       }
    }

# output tables
output_tables_config = {
    'hidden_tables': list(),
    'categories': dict(),
    'order': list(),
    'tables_display_names': dict(),
    'columns_display_names': dict(),
    'hidden_columns': dict()
    }










