User Inputs and Reporting
=========================

This page summarizes the information a user should prepare before running VITAL
and explains how to export results for review, sharing, or archival.

VITAL is intended for screening-level analysis of tidal energy systems integrated
with vessels, floating platforms, or other deployable marine-energy
infrastructure. Results should be used for early-stage comparison of sites and
design assumptions, not as final engineering, permitting, or deployment
recommendations.

Units and File Format Conventions
---------------------------------

Unless otherwise noted, VITAL expects SI units for physical and engineering
inputs.

Common units used by VITAL are:

.. list-table::
   :header-rows: 1

   * - Quantity
     - Expected unit
     - Notes
   * - Length, radius, depth, distance
     - meters, ``m``
     - Used for rotor radius, hub depth, mooring distance, cable length, vessel dimensions
   * - Time
     - seconds, ``s``
     - Used for time vectors in local tidal files and simulation results
   * - Flow speed
     - meters per second, ``m/s``
     - Used for tidal current speed
   * - Force
     - newtons, ``N``
     - Used for turbine thrust, drag, mooring force, and constraint checks
   * - Torque
     - newton-meters, ``N m``
     - Used for rated generator torque
   * - Power
     - watts, ``W``
     - Used for rated power and instantaneous electrical power
   * - Energy
     - kilowatt-hours, ``kWh``
     - Used for annual energy and battery capacity
   * - Cost
     - U.S. dollars, ``USD``
     - Used for CAPEX, OPEX, and cost breakdowns
   * - LCOE
     - ``USD/kWh``
     - Levelized cost of energy
   * - Angles
     - radians, ``rad``
     - Used internally for vessel and mooring angles
   * - Latitude and longitude in user metadata
     - decimal degrees
     - Converted internally to radians where needed
   * - Density
     - ``kg/m^3``
     - Used for vessel or material density
   * - Area
     - ``m^2``
     - Used for vessel drag area
   * - Volume
     - ``m^3``
     - Used for vessel or displaced volume
   * - Coefficients
     - dimensionless
     - Examples include ``TSR``, ``Ct``, ``Cq``, ``Cp``, ``Cd``, and turbulence intensity

Recommended file extensions are:

.. list-table::
   :header-rows: 1

   * - Input or output
     - Recommended file type
     - Notes
   * - Local tidal resource data
     - ``.txt`` or ``.dat``
     - Whitespace-delimited text with columns ``t`` and ``U``
   * - Rotor performance data
     - ``.txt`` or ``.dat``
     - Whitespace- or tab-delimited text with columns ``TSR``, ``Ct``, and ``Cq``
   * - Cpmin data
     - ``.json``
     - Optional JSON file with ``TSR`` and ``Cpmin`` entries
   * - City metadata
     - ``.csv`` or ``.txt``
     - Comma-separated file with ``Name``, ``Latitude``, and ``Longitude``
   * - Exported report
     - ``.md``
     - Markdown summary for human review
   * - Exported summary table
     - ``.csv``
     - Machine-readable summary or result table

Quick User Checklist
--------------------

Before starting a VITAL analysis, gather the following information:

.. list-table::
   :header-rows: 1

   * - Input
     - Required?
     - Format
     - Units
     - Notes
   * - Tidal resource data
     - Yes
     - NOAA station request or local whitespace-delimited file
     - ``m/s`` for flow speed, ``s`` for time
     - Local files require ``t`` and ``U`` columns
   * - Site metadata
     - Yes for local tidal files
     - Python dictionary
     - degrees for latitude/longitude, ``m`` for mooring/cable length
     - Required keys are listed below
   * - City metadata
     - Optional
     - CSV-like file
     - decimal degrees for coordinates
     - Required columns are ``Name``, ``Latitude``, and ``Longitude``
   * - Rotor performance data
     - Yes
     - Whitespace- or tab-delimited text file
     - dimensionless coefficients
     - Required columns are ``TSR``, ``Ct``, and ``Cq``
   * - Cpmin data
     - Optional
     - JSON file
     - dimensionless
     - Used for cavitation-related checks if available
   * - Turbine configuration
     - Yes
     - Python dictionary
     - SI units
     - Includes radius, rated power, hub depth, time series, and rotor interpolation functions
   * - Vessel or platform properties
     - Yes
     - Defaults or Python dictionary
     - SI units
     - Used for drag and physical constraint checks
   * - Application type
     - Yes
     - String
     - Not applicable
     - Common examples are ``battery_charging`` and ``grid_connection``
   * - Battery capacity
     - Required for battery charging
     - Numeric value
     - ``kWh``
     - Use ``BatteryCapacity_kWh``
   * - Project economics
     - Yes
     - Numeric values and strings
     - years, fraction, USD
     - Includes lifetime, discount rate, customer, and application
   * - Optimization bounds
     - Required for optimization only
     - Python dictionary
     - Same units as the design variable
     - Each variable uses ``(minimum, maximum, step)``

Required User Inputs
--------------------

A typical VITAL workflow requires five categories of user input:

1. tidal resource data
2. rotor performance data
3. turbine configuration assumptions
4. vessel or platform properties
5. project and cost-model assumptions

The exact inputs depend on the workflow being used. For example,
battery-charging workflows require a battery capacity, while grid-connected
workflows do not.

Tidal Resource Data
-------------------

VITAL can use tidal resource data from NOAA or from a local file.

NOAA-based workflow
~~~~~~~~~~~~~~~~~~~

For the NOAA workflow, the user provides:

.. list-table::
   :header-rows: 1

   * - Input
     - Type
     - Units or format
     - Description
   * - ``station``
     - string
     - NOAA station identifier
     - Station ID used to request current prediction data
   * - ``startdate``
     - string
     - ``YYYY-MM-DD``
     - Start date for the NOAA data request
   * - ``range_hrs``
     - integer or float
     - hours
     - Requested time range
   * - ``time_step_s``
     - integer or float
     - seconds
     - Time step used for interpolation

Example:

.. code-block:: python

   tidal = process_tidal_data(
       station="SEA0838",
       startdate="2023-01-01",
       range_hrs=24 * 14,
       time_step_s=3600,
       city_data_file="../data/AlaskaCityLatLong.txt",
   )

The tidal-data processing function returns a processed object containing:

.. list-table::
   :header-rows: 1

   * - Returned field
     - Units
     - Description
   * - ``flow_speeds``
     - ``m/s``
     - Tidal flow-speed time series
   * - ``times``
     - ``s``
     - Time vector
   * - ``mooring_distance``
     - ``m``
     - Mooring depth or distance
   * - ``latitude``
     - radians
     - Station latitude converted for internal calculations
   * - ``longitude``
     - radians
     - Station longitude converted for internal calculations
   * - ``station_name``
     - string
     - Station name
   * - ``nearest_city``
     - string
     - Nearest city identified from the city metadata file, if available
   * - ``cable_length``
     - ``m``
     - Estimated electrical cable length
   * - ``source``
     - string
     - ``"NOAA"`` or ``"local_file"``

Local-file workflow
~~~~~~~~~~~~~~~~~~~

For offline or reproducible studies, users may provide a local tidal data file.

Recommended file type:

- ``.txt`` or ``.dat``
- whitespace-delimited
- first row should contain column names
- required columns are ``t`` and ``U``

The local tidal file must contain at least these columns:

.. list-table::
   :header-rows: 1

   * - Column
     - Type
     - Units
     - Description
   * - ``t``
     - numeric
     - seconds, ``s``
     - Time vector. Values should be monotonically increasing.
   * - ``U``
     - numeric
     - meters per second, ``m/s``
     - Tidal flow speed. VITAL uses the absolute value internally.

Example local tidal file:

.. code-block:: text

   t U
   0 0.85
   3600 1.10
   7200 0.95
   10800 0.40

When using a local tidal file, the user must also provide site metadata because
the station information is no longer coming from NOAA.

Required local-file metadata:

.. list-table::
   :header-rows: 1

   * - Metadata key
     - Type
     - Units or format
     - Description
   * - ``station_name``
     - string
     - text
     - Name or label for the site
   * - ``latitude_deg``
     - numeric
     - decimal degrees
     - Site latitude
   * - ``longitude_deg``
     - numeric
     - decimal degrees
     - Site longitude
   * - ``mooring_distance_m``
     - numeric
     - meters, ``m``
     - Mooring depth or distance used by the vessel/turbine model

Optional local-file metadata:

.. list-table::
   :header-rows: 1

   * - Metadata key
     - Type
     - Units or format
     - Description
   * - ``nearest_city``
     - string
     - text
     - User-specified nearest city label
   * - ``cable_length_m``
     - numeric
     - meters, ``m``
     - Electrical cable length used by the cost model

Example:

.. code-block:: python

   tidal = process_tidal_data(
       station="LOCAL_SITE_001",
       startdate="2023-01-01",
       range_hrs=336,
       time_step_s=3600,
       local_file="local_tidal_site_001.txt",
       fallback_metadata={
           "station_name": "Local Site 001",
           "latitude_deg": 57.05,
           "longitude_deg": -135.34,
           "mooring_distance_m": 31.1,
           "nearest_city": "Sitka",
           "cable_length_m": 3970.22,
       },
   )

City metadata file
~~~~~~~~~~~~~~~~~~

If a city-data file is supplied, VITAL can estimate the nearest city and cable
length from the supplied latitude and longitude.

Recommended file type:

- ``.csv`` or comma-separated ``.txt``

Required columns:

.. list-table::
   :header-rows: 1

   * - Column
     - Type
     - Units or format
     - Description
   * - ``Name``
     - string
     - text
     - City or community name
   * - ``Latitude``
     - numeric
     - decimal degrees
     - City latitude
   * - ``Longitude``
     - numeric
     - decimal degrees
     - City longitude

Example city metadata file:

.. code-block:: text

   Name,Latitude,Longitude
   Sitka,57.0531,-135.3300
   Juneau,58.3019,-134.4197

Rotor Performance Data
----------------------

Rotor performance data are loaded using ``RotorData``.

Recommended file type:

- ``.txt`` or ``.dat``
- whitespace-delimited or tab-delimited text
- first row should contain column names

The rotor performance file must contain at least these columns:

.. list-table::
   :header-rows: 1

   * - Column
     - Type
     - Units
     - Description
   * - ``TSR``
     - numeric
     - dimensionless
     - Tip-speed ratio
   * - ``Ct``
     - numeric
     - dimensionless
     - Thrust coefficient
   * - ``Cq``
     - numeric
     - dimensionless
     - Torque coefficient

Example rotor performance file:

.. code-block:: text

   TSR Ct Cq
   0.0 0.10 0.000
   1.0 0.45 0.120
   2.0 0.70 0.180
   3.0 0.82 0.160
   4.0 0.78 0.120

VITAL computes the power coefficient internally as:

.. math::

   C_p = TSR \cdot C_q

Therefore, the input rotor data file does not need to include a ``Cp`` column.
Some rotor files may include ``Cp`` for reference, but VITAL recomputes
``Cp`` from ``TSR`` and ``Cq``.

The rotor data should span the expected operating range of tip-speed ratios.
Values outside the provided range are handled by simplified extrapolation logic
and should not be interpreted as validated rotor performance.

Cpmin Data
~~~~~~~~~~

If cavitation checks are important for the study, users may also provide
``Cpmin`` data.

Recommended file type:

- ``.json``

Expected structure:

.. code-block:: json

   {
     "TSR": [0.0, 1.0, 2.0, 3.0],
     "Cpmin": {
       "0": [-0.2, -0.5, -0.8, -1.0]
     }
   }

Expected units:

.. list-table::
   :header-rows: 1

   * - Field
     - Units
     - Description
   * - ``TSR``
     - dimensionless
     - Tip-speed-ratio values corresponding to the Cpmin curve
   * - ``Cpmin``
     - dimensionless
     - Minimum pressure coefficient values

If no ``Cpmin`` file is supplied, VITAL uses a default ``Cpmin`` assumption.

Turbine Configuration
---------------------

The turbine configuration is provided as a Python dictionary. VITAL expects the
dictionary values to use SI units.

Required fields for LCOE calculations include ``Radius``, ``Prated``,
``number_of_turbines``, and ``dHub``. Most complete simulation workflows also
include time-series inputs and rotor interpolation functions.

Common fields include:

.. list-table::
   :header-rows: 1

   * - Field
     - Type
     - Units
     - Required?
     - Description
   * - ``Radius``
     - numeric
     - meters, ``m``
     - Yes
     - Rotor radius
   * - ``Prated``
     - numeric
     - watts, ``W``
     - Yes
     - Rated electrical power per turbine
   * - ``Trated``
     - numeric
     - newton-meters, ``N m``
     - Usually
     - Rated generator torque
   * - ``dHub``
     - numeric
     - meters, ``m``
     - Yes
     - Hub depth
   * - ``number_of_turbines``
     - integer
     - count
     - Yes
     - Number of turbines in the system
   * - ``dMoor``
     - numeric
     - meters, ``m``
     - Usually
     - Mooring depth or distance
   * - ``Uinf``
     - array-like
     - meters per second, ``m/s``
     - Usually
     - Tidal flow-speed time series
   * - ``t``
     - array-like
     - seconds, ``s``
     - Usually
     - Time vector corresponding to ``Uinf``
   * - ``CpFunc``
     - callable
     - dimensionless output
     - Usually
     - Power-coefficient interpolation function
   * - ``CqFunc``
     - callable
     - dimensionless output
     - Usually
     - Torque-coefficient interpolation function
   * - ``CtFunc``
     - callable
     - dimensionless output
     - Usually
     - Thrust-coefficient interpolation function
   * - ``CpminFunc``
     - callable
     - dimensionless output
     - Optional
     - Minimum-pressure-coefficient interpolation function
   * - ``CpOpt``
     - numeric
     - dimensionless
     - Usually
     - Optimal power coefficient
   * - ``TSROpt``
     - numeric
     - dimensionless
     - Usually
     - Optimal tip-speed ratio
   * - ``TSRmax``
     - numeric
     - dimensionless
     - Usually
     - Maximum tip-speed ratio used by the simulation

Depending on the selected power-conversion model, additional parameters may be
required. For example, the simple electrical model uses generator and drivetrain
parameters such as ``Ng``, ``Kt``, ``Rw``, ``Bg``, and ``J_r``.

Example:

.. code-block:: python

   turbine_config = {
       "Radius": 0.5,                    # m
       "Prated": 2500.0,                 # W
       "Trated": 100.0,                  # N m
       "dHub": 2.0,                      # m
       "number_of_turbines": 2,          # count
       "dMoor": tidal.mooring_distance,  # m
       "Uinf": tidal.flow_speeds,        # m/s
       "t": tidal.times,                 # s
       "CpFunc": rotor.get_cp,
       "CqFunc": rotor.get_cq,
       "CtFunc": rotor.get_ct,
       "CpminFunc": rotor.get_cpmin,
       "CpOpt": rotor.CpOpt,
       "TSROpt": rotor.TSROpt,
       "TSRmax": rotor.TSRmax,
   }

Vessel or Platform Properties
-----------------------------

Vessel or platform properties are used for physical constraint checks and LCOE
calculations.

VITAL supports two common approaches:

1. use the default vessel assumptions by creating ``VesselData`` without a
   custom ``vessel_properties`` dictionary
2. provide a custom ``vessel_properties`` dictionary with the keys expected by
   the current implementation

All user-supplied physical values should use SI units.

Default vessel inputs
~~~~~~~~~~~~~~~~~~~~~

When using the default vessel model, users may provide optional constructor
arguments such as:

.. list-table::
   :header-rows: 1

   * - Input
     - Type
     - Units
     - Description
   * - ``height``
     - numeric
     - meters, ``m``
     - Vessel or platform height
   * - ``density``
     - numeric
     - kilograms per cubic meter, ``kg/m^3``
     - Representative vessel or platform density
   * - ``theta_m``
     - numeric
     - radians, ``rad``
     - Mooring-line angle
   * - ``alpha``
     - numeric
     - dimensionless
     - Aspect-ratio parameter used by the simplified vessel model
   * - ``Cd``
     - numeric
     - dimensionless
     - Drag coefficient
   * - ``phi``
     - numeric
     - radians, ``rad``
     - Pitch angle or pitch constraint used by the constraint model
   * - ``simResult``
     - dictionary
     - SI units
     - Optional simulation result used to estimate drag force from adjusted inflow speed

Example:

.. code-block:: python

   vessel = VesselData(
       height=2.0,                # m
       density=500.0,             # kg/m^3
       theta_m=np.pi / 4.0,       # rad
       alpha=2.0,                 # dimensionless
       Cd=1.0,                    # dimensionless
       phi=10.0 * np.pi / 180.0,  # rad
       simResult=sim_result,
   )

Custom vessel-property dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For a fully custom vessel definition, create ``VesselData`` with
``user_defined=True`` and provide a ``vessel_properties`` dictionary.

The current implementation expects the following dictionary keys:

.. list-table::
   :header-rows: 1

   * - Key
     - Type
     - Units
     - Required?
     - Description
   * - ``Xm``
     - numeric
     - meters, ``m``
     - Yes
     - Longitudinal or horizontal reference location used by the constraint model
   * - ``Zm``
     - numeric
     - meters, ``m``
     - Yes
     - Vertical reference location used by the constraint model
   * - ``Kphi``
     - numeric
     - rotational stiffness, typically ``N m/rad``
     - Yes
     - Pitch hydrostatic stiffness used by the constraint model
   * - ``theta``
     - numeric
     - radians, ``rad``
     - Yes
     - Mooring-line angle
   * - ``phi``
     - numeric
     - radians, ``rad``
     - Yes
     - Pitch angle used for constraint evaluation
   * - ``area``
     - numeric
     - square meters, ``m^2``
     - Yes
     - Cross-sectional area used for drag calculation
   * - ``Cd``
     - numeric
     - dimensionless
     - Yes
     - Drag coefficient

Example:

.. code-block:: python

   user_vessel_properties = {
       "Xm": 0.0,                         # m
       "Zm": 0.0,                         # m
       "Kphi": 1.0e6,                     # N m/rad
       "theta": 45.0 * np.pi / 180.0,     # rad
       "phi": 10.0 * np.pi / 180.0,       # rad
       "area": 9.5,                       # m^2
       "Cd": 1.0,                         # dimensionless
   }

   vessel = VesselData(
       user_defined=True,
       vessel_properties=user_vessel_properties,
       simResult=sim_result,
   )

If any required custom vessel key is missing, VITAL raises an error when setting
the vessel properties.

Notes on vessel assumptions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The default vessel model may also calculate or store additional quantities such
as width, length, hydrostatic stiffness, metacentric height, displaced volume,
submerged height, and drag force. These values are part of the simplified vessel
model and are not all required as direct user inputs.

Users should review vessel assumptions carefully. Simplified vessel or platform
properties can be useful for screening studies, but they may not represent a
final deployable design.

LCOE Inputs
-----------

The ``LCOEData`` object collects the inputs required by ``LCOECalculator``.

Expected inputs include:

.. list-table::
   :header-rows: 1

   * - Input
     - Type
     - Units or allowed values
     - Description
   * - ``tidalData``
     - processed tidal-data object
     - SI units
     - Contains cable length, mooring distance, flow speeds, and time values
   * - ``turbineConfig``
     - dictionary
     - SI units
     - Contains turbine geometry, rated power, and operating assumptions
   * - ``vesselData``
     - ``VesselData`` object
     - SI units
     - Contains vessel/platform properties and drag force
   * - ``simResult``
     - dictionary
     - ``Pelec`` in W, ``t`` in s
     - Simulation result containing power and time data
   * - ``lifetime``
     - integer or float
     - years
     - Project lifetime used in present-value calculations
   * - ``discount_rate``
     - numeric
     - fraction
     - Example: use ``0.08`` for 8%
   * - ``turbulence_intensity``
     - numeric
     - fraction
     - Example: use ``0.10`` for 10%
   * - ``customer``
     - string
     - configured customer key
     - Selects the cost-function configuration
   * - ``application``
     - string
     - configured application key
     - Common examples are ``battery_charging`` and ``grid_connection``
   * - ``BatteryCapacity_kWh``
     - numeric or ``None``
     - kilowatt-hours, ``kWh``
     - Required for battery-charging applications

Supported application examples include:

- ``application="battery_charging"``
- ``application="grid_connection"``

For ``application="battery_charging"``, ``BatteryCapacity_kWh`` must be provided
and must be greater than zero.

For ``application="grid_connection"``, battery capacity is internally treated as
zero.

Example:

.. code-block:: python

   lcoe_data = LCOEData(
       tidalData=tidal,
       turbineConfig=turbine_config,
       vesselData=vessel,
       simResult=sim_result,
       lifetime=10,                    # years
       discount_rate=0.10,             # fraction
       turbulence_intensity=0.0,       # fraction
       customer="customer_B",
       application="battery_charging",
       BatteryCapacity_kWh=10.0,       # kWh
   )

Simulation Result Inputs
------------------------

Some workflows create ``simResult`` by running ``RotorSimulation``. If a user
constructs or modifies ``simResult`` manually, it must contain at least:

.. list-table::
   :header-rows: 1

   * - Key
     - Type
     - Units
     - Description
   * - ``Pelec``
     - array-like
     - watts, ``W``
     - Electrical power time series
   * - ``t``
     - array-like
     - seconds, ``s``
     - Time vector corresponding to ``Pelec``

Many workflows also use:

.. list-table::
   :header-rows: 1

   * - Key
     - Units
     - Description
   * - ``Ft``
     - newtons, ``N``
     - Turbine thrust time series
   * - ``Uinf_adjusted``
     - meters per second, ``m/s``
     - Adjusted inflow velocity time series

The ``Pelec`` and ``t`` arrays must have the same length.

Optimization Inputs
-------------------

The LCOE optimizer performs an explicit grid search over selected design
variables.

The user provides ``variable_bounds`` as a Python dictionary. Each entry maps a
design variable to a tuple of:

.. code-block:: python

   (minimum, maximum, step)

The units of ``minimum``, ``maximum``, and ``step`` must match the units of the
design variable being optimized.

Example:

.. code-block:: python

   variable_bounds = {
       "Radius": (0.5, 1.0, 0.25),        # m
       "Prated": (1000.0, 5000.0, 2000.0) # W
   }

Common optimization variables include:

.. list-table::
   :header-rows: 1

   * - Variable
     - Units
     - Description
   * - ``Radius``
     - ``m``
     - Rotor radius
   * - ``Prated``
     - ``W``
     - Rated electrical power
   * - ``dHub``
     - ``m``
     - Hub depth
   * - ``number_of_turbines``
     - count
     - Number of turbines

The optimizer evaluates each combination in the grid. The total number of
evaluated designs is the product of the number of values for each variable.
Fine step sizes or many design variables can create large numbers of
simulations.

Users may also provide:

.. list-table::
   :header-rows: 1

   * - Input
     - Type
     - Units or format
     - Description
   * - ``fixed_params``
     - dictionary
     - same units as fixed variables
     - Parameters held constant during the optimization
   * - ``site_params``
     - dictionary
     - SI units
     - Site-specific values such as ``dMoor``, ``Uinf``, and ``t``
   * - ``customer``
     - string
     - configured customer key
     - Selects cost functions
   * - ``application``
     - string
     - configured application key
     - Example: ``battery_charging`` or ``grid_connection``
   * - ``BatteryCapacity_kWh``
     - numeric
     - ``kWh``
     - Required for battery-charging optimization
   * - ``lifetime``
     - integer or float
     - years
     - Project lifetime
   * - ``discount_rate``
     - numeric
     - fraction
     - Example: ``0.08`` for 8%
   * - ``turbulence_intensity``
     - numeric
     - fraction
     - Example: ``0.10`` for 10%

Example:

.. code-block:: python

   opt_result = optimizer.optimize(
       variable_bounds=variable_bounds,
       fixed_params=fixed_params,
       site_params={
           "dMoor": tidal.mooring_distance,  # m
           "Uinf": tidal.flow_speeds,        # m/s
           "t": tidal.times,                 # s
       },
       customer="customer_B",
       application="battery_charging",
       BatteryCapacity_kWh=10.0,             # kWh
       lifetime=10,                          # years
       discount_rate=0.10,                   # fraction
       turbulence_intensity=0.0,             # fraction
   )

Reporting and Exported Files
----------------------------

VITAL includes lightweight reporting helpers in ``vital.module_reporting``.

These helpers export results to:

.. list-table::
   :header-rows: 1

   * - Export type
     - File extension
     - Intended use
   * - Markdown report
     - ``.md``
     - Human-readable summary for review, sharing, or project records
   * - CSV summary
     - ``.csv``
     - Machine-readable summary for downstream analysis or archival
   * - Full optimization table
     - ``.csv``
     - All evaluated design points
   * - Feasible optimization table
     - ``.csv``
     - Evaluated design points that passed feasibility checks

LCOE Reports
~~~~~~~~~~~~

Use ``export_lcoe_report`` to export a report from an initialized
``LCOECalculator``:

.. code-block:: python

   from vital.module_reporting import export_lcoe_report

   report_files = export_lcoe_report(
       calculator,
       output_prefix="reports/quickstart_lcoe_summary",
   )

   print(report_files["markdown"])
   print(report_files["csv"])

This creates:

.. code-block:: text

   reports/quickstart_lcoe_summary.md
   reports/quickstart_lcoe_summary.csv

The LCOE Markdown report includes:

.. list-table::
   :header-rows: 1

   * - Report item
     - Units
     - Description
   * - LCOE
     - ``USD/kWh``
     - Levelized cost of energy
   * - Annual energy
     - ``kWh/year``
     - Estimated annual electrical energy production
   * - Capacity factor
     - dimensionless
     - Ratio of generated annual energy to rated annual energy
   * - Adjusted CAPEX
     - ``USD``
     - Total capital cost after any customer/application adjustment
   * - Annual OPEX
     - ``USD/year``
     - Annual operating cost
   * - Turbine radius
     - ``m``
     - Rotor radius
   * - Rated power
     - ``W``
     - Rated electrical power
   * - Hub depth
     - ``m``
     - Turbine hub depth
   * - Cable length
     - ``m``
     - Electrical cable length used in the cost model
   * - Mooring depth
     - ``m``
     - Mooring depth or distance used in the cost model
   * - Battery capacity
     - ``kWh``
     - Battery capacity for battery-charging applications
   * - CAPEX breakdown
     - ``USD``
     - Individual cost components

The CSV file contains the same summary information in machine-readable form.

Optimization Reports
~~~~~~~~~~~~~~~~~~~~

Use ``export_optimization_report`` to export a report from an optimizer result:

.. code-block:: python

   from vital.module_reporting import export_optimization_report

   report_files = export_optimization_report(
       opt_result,
       output_prefix="reports/optimization_summary",
   )

   print(report_files["markdown"])
   print(report_files["summary_csv"])
   print(report_files["all_designs_csv"])
   print(report_files["feasible_designs_csv"])

This creates:

.. code-block:: text

   reports/optimization_summary.md
   reports/optimization_summary.csv
   reports/optimization_summary_all_designs.csv
   reports/optimization_summary_feasible_designs.csv

The optimization Markdown report includes:

.. list-table::
   :header-rows: 1

   * - Report item
     - Units
     - Description
   * - Optimal LCOE
     - ``USD/kWh``
     - Lowest feasible LCOE found in the grid search
   * - Total designs
     - count
     - Total number of evaluated grid points
   * - Feasible designs
     - count
     - Number of evaluated designs that were feasible
   * - Feasible fraction
     - dimensionless
     - Feasible designs divided by total designs
   * - Optimal design variables
     - same units as input variables
     - Design-variable values associated with the optimal feasible result

The optimization CSV files include:

- a compact optimization summary
- the full table of evaluated designs
- the subset of feasible designs

Where Reports Are Saved
~~~~~~~~~~~~~~~~~~~~~~~

Reports are written relative to the current Python working directory.

For example:

.. code-block:: python

   output_prefix="reports/quickstart_lcoe_summary"

writes files to:

.. code-block:: text

   reports/

To see the exact location from a notebook, run:

.. code-block:: python

   from pathlib import Path

   for path in Path("reports").rglob("*"):
       print(path.resolve())

Markdown files can be opened in a text editor, viewed in JupyterLab or VS Code, or converted to other formats using standard Markdown tooling.

Recommended Project Information to Record
-----------------------------------------

For reproducible studies, users should record:

.. list-table::
   :header-rows: 1

   * - Information to record
     - Units or format
     - Why it matters
   * - VITAL version or Git commit
     - text
     - Identifies the software version used
   * - Analysis date
     - date
     - Supports traceability
   * - Analyst name or project identifier
     - text
     - Supports review and archival
   * - Tidal-data source
     - NOAA or local file
     - Identifies the source of resource data
   * - NOAA station ID or local-file name
     - text
     - Supports repeatability
   * - Start date, time range, and ``time_step_s`` value
     - date, hours, seconds
     - Defines the tidal-data period and resolution
   * - Rotor performance file name
     - file path
     - Identifies the rotor performance curve
   * - Cpmin file name, if used
     - file path
     - Identifies cavitation-related data
   * - Turbine configuration
     - SI units
     - Defines the modeled turbine system
   * - Vessel/platform assumptions
     - SI units
     - Defines the modeled vessel or platform
   * - Customer and application type
     - strings
     - Selects the cost model and application assumptions
   * - Project lifetime
     - years
     - Used in present-value calculations
   * - Discount rate
     - fraction
     - Used in present-value calculations
   * - Battery capacity, if applicable
     - ``kWh``
     - Required for battery-charging applications
   * - Optimization variable bounds, if applicable
     - same units as variables
     - Defines the optimization search space
   * - Notes about assumptions or exclusions
     - text
     - Helps reviewers interpret screening-level results

Interpreting Reports
--------------------

The exported reports are intended for communication and review. They do not
replace review of the underlying model inputs, assumptions, constraints, or
simulation outputs.

Before using a report to compare designs or sites, users should confirm that:

- the tidal data source and time range are appropriate
- local tidal files use ``t`` in seconds and ``U`` in ``m/s``
- rotor performance data are applicable to the design being studied
- rotor performance files include ``TSR``, ``Ct``, and ``Cq``
- vessel or platform assumptions are representative
- angles are supplied in radians where required by the Python model
- constraint checks have been reviewed
- cost assumptions are appropriate for the use case
- the customer and application type are correct
- battery capacity is specified in ``kWh`` for battery-charging studies
- optimization bounds and step sizes use the same units as the design variables
- the exported Markdown and CSV files are archived with the input data used to create them

Reports should be treated as screening-level summaries.