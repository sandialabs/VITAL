from module_cost_calculations import (
    calculate_blade_cost,
    calculate_generator_cost,
    calculate_electrical_cable_cost,
    calculate_grid_connection_cost,
    calculate_mooring_cost,
    calculate_misc_cost,
    calculate_hub_cost,
    calculate_cable_installation_cost,
    calculate_rotor_cost_SITKANA,
    calculate_rotor_construction_cost_SITKANA,
    calculate_steel_component_cost_SITKANA,
    calculate_generator_cost_SITKANA,
    calculate_assembly_cost_SITKANA,
    calculate_concrete_cost_SITKANA,
    calculate_gearbox_cost_SITKANA,
    calculate_charge_controller_cost_SITKANA,
    calculate_platform_cost_SITKANA,
    calculate_anchor_cost_SITKANA,
    # calculate_electrical_cable_cost_SITKANA,
    calculate_battery_cost_SITKANA
)

# Configuration dictionary for different customers and applications
COST_FUNCTIONS = {
    'customer_A': {
        'rotor_and_drivetrain': {
            'blade_cost': calculate_blade_cost,
            'generator_cost': calculate_generator_cost,
            'misc_cost': calculate_misc_cost,
            'mooring_cost': calculate_mooring_cost
        },
        'applications': {
            'grid_connection': {
                'electrical_cable_cost': calculate_electrical_cable_cost,
                'grid_connection_cost': calculate_grid_connection_cost,
                'hub_cost': calculate_hub_cost,
                'cable_installation_cost': calculate_cable_installation_cost
            },
            'battery_charging': {
                'battery_cost': calculate_battery_cost_SITKANA
            }
        }
    },
    'customer_B': {
        'rotor_and_drivetrain': {
            'anchor_cost': calculate_anchor_cost_SITKANA,
            # 'platform_cost': calculate_platform_cost_SITKANA,
            'charge_controller_cost': calculate_charge_controller_cost_SITKANA,
            'gearbox_cost': calculate_gearbox_cost_SITKANA,
            'concrete_cost': calculate_concrete_cost_SITKANA,
            'assembly_cost': calculate_assembly_cost_SITKANA,
            'generator_cost': calculate_generator_cost_SITKANA,
            'rotor_cost': calculate_rotor_cost_SITKANA,
            'steel_component_cost': calculate_steel_component_cost_SITKANA,
            'rotor_construction_cost': calculate_rotor_construction_cost_SITKANA
        },
        'applications': {
            'grid_connection': {
                'electrical_cable_cost': calculate_electrical_cable_cost,
                'grid_connection_cost': calculate_grid_connection_cost,
                'hub_cost': calculate_hub_cost,
                'cable_installation_cost': calculate_cable_installation_cost
            },
            'battery_charging': {
                'battery_cost': calculate_battery_cost_SITKANA
            }
        }
    }
}
