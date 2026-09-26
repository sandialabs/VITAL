"""
vital: A package for managing tidal energy systems, rotor simulations, vessel data, and more.

This package provides modules for:
    * Handling tidal data (`module_tidal`)
    * Rotor simulations (`module_rotor` and `module_rotor_simulation`)
    * Constraint checking (`module_constraint_checker`)
    * Vessel operations (`module_vessel`)
    * Levelized cost of energy (LCOE) calculations (`module_lcoe` and `module_lcoe_optimizer`)
    * Battery charging systems
    * Reporting utilities (`module_reporting`)

It also includes:
    * Global physical constants (`constGlobal`)
    * Unit conversion constants (`constUnitConvert`)
    * Reporting helpers for stakeholder-readable Markdown and CSV outputs

Modules:
    * `constUnitConvert`: Provides unit conversion constants.
    * `constGlobal`: Provides global physical constants.
    * `module_tidal`: Handles tidal data retrieval and processing.
    * `module_rotor`: Manages rotor performance data.
    * `module_rotor_simulation`: Simulates rotor behavior under various conditions.
    * `module_constraint_checker`: Checks constraints for tidal energy systems.
    * `module_vessel`: Manages vessel data and operations.
    * `module_lcoe`: Calculates levelized cost of energy (LCOE).
    * `module_lcoe_optimizer`: Optimizes LCOE calculations.
    * `module_reporting`: Exports LCOE and optimization summaries to Markdown and CSV.

Classes:
    * `TidalData`: Handles tidal data retrieval and processing.
    * `RotorData`: Manages rotor performance data.
    * `RotorSimulation`: Simulates rotor behavior under various conditions.
    * `ConstraintChecker`: Checks constraints for tidal energy systems.
    * `VesselData`: Manages vessel data and operations.
    * `LCOEData`: Represents data required for LCOE calculations.
    * `LCOECalculator`: Performs LCOE calculations.
    * `LCOEOptimizer`: Optimizes LCOE calculations.

Constants:
    * `CONVERT`: Unit conversion constants.
    * `GLOBAL`: Global physical constants.
"""

from .constUnitConvert import ConstantsUnitConversion
from .constGlobal import ConstantsGlobal
from .module_tidal import TidalData
from .module_rotor import RotorData
from .module_rotor_simulation import RotorSimulation
from .module_constraint_checker import ConstraintChecker
from .module_vessel import VesselData
from .module_lcoe import LCOEData, LCOECalculator
from .module_lcoe_optimizer import LCOEOptimizer
from .module_reporting import (
    summarize_lcoe,
    export_lcoe_report,
    summarize_optimization_result,
    export_optimization_report,
)

# Initialize global constants for physical properties
GLOBAL = ConstantsGlobal()

# Initialize unit conversion constants
CONVERT = ConstantsUnitConversion()

# Expose the classes and constants directly
__all__ = [
    # Classes
    "TidalData",
    "RotorData",
    "RotorSimulation",
    "ConstraintChecker",
    "VesselData",
    "LCOEData",
    "LCOECalculator",
    "LCOEOptimizer",

    # Reporting helpers
    "summarize_lcoe",
    "export_lcoe_report",
    "summarize_optimization_result",
    "export_optimization_report",

    # Constants
    "CONVERT",
    "GLOBAL",
]