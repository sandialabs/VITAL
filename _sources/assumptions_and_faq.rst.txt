Assumptions and FAQ
===================

This page summarizes important assumptions, simplifications, default values, and common questions for users of VITAL.

The details below are provided to help users interpret screening-level results and understand where additional engineering review may be needed.

General Scope
-------------

What is VITAL intended to do?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

VITAL is intended to support early-stage assessment of tidal turbine systems integrated with vessels or floating platforms. It combines tidal resource processing, rotor performance data, rotor dynamic simulation, vessel loading, constraint checking, cost estimation, and LCOE calculation.

The tool is designed for comparative analysis and screening studies. It is not a substitute for detailed engineering design, certification, environmental review, or site-specific permitting analysis.

What applications are currently represented?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The software includes cost configuration support for:

- Battery charging applications.
- Grid connection applications.

However, some application-specific models are simplified and should be reviewed before use in decision-critical studies.

What global physical constants are used?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following global physical constants are defined in ``constGlobal.py``:

.. list-table:: Global physical constants
   :header-rows: 1
   :widths: 30 30 40

   * - Quantity
     - Symbol / variable
     - Default value
   * - Seawater density
     - ``rho``
     - ``1025.0 kg/m^3``
   * - Atmospheric pressure
     - ``Patm``
     - ``101325.0 Pa``
   * - Seawater vapor pressure at 25 deg C
     - ``Pvap``
     - ``3063.7485 Pa``
   * - Gravitational acceleration
     - ``g``
     - ``9.8 m/s^2``

These constants are used in hydrodynamic force calculations, cavitation checks, and flow-related calculations.

Tidal Data
----------

Where does tidal data come from?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``module_tidal`` workflow attempts to retrieve tidal current predictions from NOAA APIs. If NOAA access fails and a local fallback file is supplied, the workflow can use local tidal data instead.

The high-level function is:

.. code-block:: python

   process_tidal_data(
       station,
       startdate,
       range_hrs=2 * 7 * 24,
       time_step_s=3600,
       city_data_file="../data/AlaskaCityLatLong.txt",
       local_file=None,
       fallback_metadata=None,
   )

What are the default tidal-data processing values?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following defaults are used by ``process_tidal_data`` and ``module_tidal.py``:

.. list-table:: Tidal-data defaults
   :header-rows: 1
   :widths: 35 30 35

   * - Quantity
     - Variable
     - Default value
   * - Time range
     - ``range_hrs``
     - ``2 * 7 * 24 = 336 hr``
   * - Interpolated time step
     - ``time_step_s``
     - ``3600 s``
   * - City data file
     - ``city_data_file``
     - ``"../data/AlaskaCityLatLong.txt"``
   * - Minimum flow speed floor
     - ``MIN_FLOW_SPEED``
     - ``1e-4 m/s``
   * - Default mooring distance
     - ``DEFAULT_MOORING_DISTANCE_M``
     - ``50.0 m``
   * - Earth radius for distance calculations
     - ``EARTH_RADIUS_M``
     - ``6378137.0 m``

The NOAA request internally extends the requested range by 2 hours before interpolation. For example, if ``range_hrs = 336``, the NOAA request uses ``338`` hours. This helps provide enough data for interpolation at the end of the requested interval.

What units are used for tidal speed?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

NOAA current prediction speeds are converted internally from cm/s to m/s using:

.. math::

   1 \; \text{cm/s} = 10^{-2} \; \text{m/s}

Local fallback files should provide speed directly in m/s.

Why are flow speeds made nonnegative?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The current implementation uses the magnitude of flow speed by applying an absolute value:

.. code-block:: python

   self.flow_speeds_m_s = np.abs(self.flow_speeds_m_s)

This means flow reversal direction is not explicitly modeled. The rotor simulation treats the input as a speed magnitude rather than a signed vector velocity.

Is there a minimum flow speed?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes. A small minimum speed floor is applied to avoid numerical issues in interpolation and rotor dynamics calculations:

.. math::

   U_{\min} = 10^{-4} \; \text{m/s}

This value is defined as ``MIN_FLOW_SPEED = 1e-4`` in ``module_tidal.py``.

How is mooring distance determined?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For most NOAA stations, the code attempts to retrieve deployment depth information. If depth is unavailable, a default mooring distance is used:

.. math::

   d_{moor,default} = 50.0 \; \text{m}

For older station IDs beginning with ``PCT``, the code uses station metadata and applies the same default mooring distance of ``50.0 m``.

If NOAA reports depth in feet, the code converts it to meters using:

.. math::

   1 \; \text{ft} = 0.3048 \; \text{m}

How is cable length estimated?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Cable length is estimated as the great-circle distance between the tidal station/buoy location and the nearest city in the provided city metadata file.

The calculation uses:

.. math::

   R_{Earth} = 6378137.0 \; \text{m}

This is a simplified estimate and does not represent actual cable routing, bathymetry, landfall constraints, permitting constraints, installation feasibility, or final engineering design.

What local fallback data format is expected?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If NOAA data are unavailable, a local fallback file can be supplied. The local file must be whitespace-delimited and contain at least the following columns:

.. list-table:: Required local tidal file columns
   :header-rows: 1
   :widths: 20 40 40

   * - Column
     - Meaning
     - Units
   * - ``t``
     - Time
     - seconds
   * - ``U``
     - Flow speed
     - m/s

Example:

.. code-block:: text

   t U
   0 0.85
   3600 1.10
   7200 0.95
   10800 0.40

When using a local fallback file, ``fallback_metadata`` must include:

- ``station_name``
- ``latitude_deg``
- ``longitude_deg``
- ``mooring_distance_m``

Optional metadata fields are:

- ``nearest_city``
- ``cable_length_m``

If ``city_data_file`` is provided, the code attempts to compute nearest city and cable length from the fallback latitude and longitude.

Rotor Data
----------

What rotor data columns are required?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The rotor performance data file must contain the following columns:

- ``TSR``
- ``Ct``
- ``Cq``

The power coefficient is computed internally as:

.. math::

   C_p = TSR \cdot C_q

What happens to negative rotor coefficients?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The rotor data are processed using the following physical sign constraints:

.. code-block:: python

   self.cq = np.maximum(self.cq, 0.0)
   self.ct = np.maximum(self.ct, 0.0)
   self.cpmin = np.minimum(self.cpmin, 0.0)
   self.cp = np.maximum(self.cp, 0.0)

Thus:

- ``Cq`` is clipped to be nonnegative.
- ``Ct`` is clipped to be nonnegative.
- ``Cp`` is clipped to be nonnegative.
- ``Cpmin`` is clipped to be nonpositive.

How are rotor coefficients interpolated?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The code uses monotonic PCHIP interpolation for ``Cq`` and ``Ct`` through ``scipy.interpolate.PchipInterpolator``.

Outside the provided TSR range, the implementation applies simplified behavior:

- Below the minimum TSR, ``Cq`` and ``Ct`` are held at the first measured value.
- Above the maximum TSR, ``Cq`` and ``Ct`` decay exponentially toward zero.

This low-TSR behavior avoids forcing ``Cq`` or ``Ct`` to zero at ``TSR = 0``. That assumption can be incorrect for drag-based turbines, where torque and thrust coefficients may be nonzero or even large at low TSR.

For the above-range exponential decay, the decay scale is based on the maximum TSR in the supplied rotor data:

.. math::

   \text{decay scale} = \max(TSR_{max,data}, 10^{-6})

Because the power coefficient is computed as:

.. math::

   C_p = TSR \cdot C_q

``Cp`` still approaches zero as ``TSR`` approaches zero, even if ``Cq`` is held nonzero below the measured TSR range.

The extrapolated values should not be interpreted as validated rotor performance. Users should provide rotor data over the expected operating TSR range whenever possible.

What happens if Cpmin data is not provided?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If no Cpmin file is provided, the code assumes:

.. math::

   C_{p,\min} = -1.0

across the TSR range.

This affects the cavitation constraint and should be replaced with rotor-specific minimum pressure coefficient data when available.

Rotor Simulation
----------------

What dynamics are modeled?
~~~~~~~~~~~~~~~~~~~~~~~~~~

The rotor simulation models generator-side angular speed using a drivetrain dynamic equation with effective inertia, friction, hydrodynamic torque, and generator torque.

The effective inertia is calculated as:

.. math::

   I_{eff} = \frac{J_r}{N_g^2} + J_d

where:

- ``J_r`` is rotor inertia.
- ``J_d`` is drivetrain inertia.
- ``N_g`` is gear ratio.

The default controller uses an optimal torque law intended to track the optimal tip-speed ratio.

What inputs are required in the rotor simulation configuration?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``RotorSimulation`` class expects the configuration dictionary to include, at minimum:

- ``Radius``
- ``Prated``
- ``Trated``
- ``dHub``
- ``dMoor``
- ``Uinf``
- ``t``
- ``CpFunc``
- ``CqFunc``
- ``CtFunc``
- ``CpOpt``
- ``TSROpt``
- ``TSRmax``
- ``Ng``
- ``J_d``
- ``B_d``
- ``J_r``

For the simple electrical power model, the configuration must also include:

- ``Kt``
- ``Rw``

What validation is performed in rotor simulation?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The rotor simulation checks several basic conditions:

.. list-table:: Rotor simulation validation
   :header-rows: 1
   :widths: 40 60

   * - Check
     - Requirement
   * - Gear ratio
     - ``Ng > 0``
   * - Rotor radius
     - ``Radius > 0``
   * - Time vector
     - ``len(t) >= 2``
   * - Optimal TSR
     - ``TSROpt > 0`` when computing ``Kopt``

What power conversion model is used by default?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The default power conversion model is:

.. code-block:: python

   power_model = "simple"

This model requires generator constants ``Kt`` and ``Rw``.

What power conversion models are supported?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The rotor simulation supports the following power-conversion options:

.. list-table:: Power conversion model options
   :header-rows: 1
   :widths: 35 65

   * - ``power_model``
     - Description
   * - ``"simple"``
     - Built-in generator electrical model using ``Kt`` and ``Rw``. No power-electronics loss model is applied.
   * - ``"simple_with_pe_loss"``
     - Built-in generator electrical model plus user-supplied power-electronics loss model.
   * - ``"generator_loss_model"``
     - User-supplied generator loss model. No power-electronics loss model is applied.
   * - ``"generator_and_pe_loss_models"``
     - User-supplied generator loss model and user-supplied power-electronics loss model.

For user-supplied generator or power-electronics loss models, the functions are assumed to use generator-side angular speed and generator torque:

- ``omega_g = self.w``
- ``tau_g = self.Tg``

What numerical solver is used?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Rotor dynamics are solved using ``scipy.integrate.solve_ivp`` with:

.. code-block:: python

   method = "Radau"

The Radau method is an implicit method suitable for stiff systems.

What happens if rated torque is exceeded?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The simulation first solves closed-loop dynamics. If the generator torque exceeds the rated torque, the torque is clipped at:

.. math::

   T_g \leq T_{rated}

The dynamics are then re-solved in open-loop mode using the clipped torque trajectory.

What is ``Pelec``?
~~~~~~~~~~~~~~~~~~

For compatibility with downstream code, ``Pelec`` is the primary electrical output used by the LCOE and constraint calculations.

In ``simple`` and ``simple_with_pe_loss`` modes, ``Pelec`` comes from the built-in generator electrical model. In these modes, ``Pac`` is calculated as nonnegative AC-side electrical power.

In ``generator_loss_model`` and ``generator_and_pe_loss_models`` modes, ``Pelec`` is treated as AC-side power and is equal to ``Pac``.

If power-electronics losses are included, battery-side power is available separately as ``Pbat``.

For battery-charging studies, users should verify whether ``Pelec``, ``Pac``, or ``Pbat`` is the appropriate power signal for their intended analysis. The current LCOE workflow uses ``Pelec`` for annual energy calculations.

Flow-at-Depth Model
-------------------

How is flow adjusted for turbine depth?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The simulation uses a simplified vertical profile correction through the ``flowAtDepth`` method. This estimates an adjusted flow speed at the rotor location based on hub depth, rotor radius, and mooring depth.

The method uses an internal average-flow scaling:

.. math::

   U_{avg} = \frac{U}{1.07}

and then estimates an equivalent velocity based on a depth-dependent power calculation.

This model is a simplification and does not fully resolve site-specific bathymetry, turbulence, shear, wave-current interaction, or three-dimensional flow effects.

Constraint Checking
-------------------

What constraints are checked?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``ConstraintChecker`` evaluates:

- Power constraint.
- Rotor submergence/depth constraint.
- Cavitation constraint.
- Vessel pitch stability constraint.

What numerical tolerances are used in constraint checks?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The power constraint uses a small tolerance of ``1e-9``:

.. code-block:: python

   Pelec >= -1e-9
   Prated - Pelec >= -1e-9

The other constraints use strict positivity:

.. code-block:: python

   depth_constraint() > 0
   cavitation_constraint() > 0
   pitch_constraint() > 0

How is the power constraint interpreted?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The electrical power must be nonnegative and must not exceed rated turbine power:

.. math::

   0 \leq P_{elec} \leq P_{rated}

In the implementation, this is checked with the ``1e-9`` numerical tolerance described above.

How is the depth constraint interpreted?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The depth constraint requires:

.. math::

   d_{hub} - R > 0

This means the top of the rotor must remain below the water surface.

How is cavitation checked?
~~~~~~~~~~~~~~~~~~~~~~~~~~

The cavitation check estimates minimum blade pressure using the supplied or default minimum pressure coefficient.

The effective velocity is estimated as:

.. math::

   V_{\infty} = \sqrt{U_{\text{inf,adjusted}}^2 + (R \omega_r)^2}

The pressure at the rotor tip is estimated using:

.. math::

   P_{\infty} = P_{atm} + \rho g (d_{hub} - R)

The cavitation constraint is implemented as:

.. math::

   h(x) =
   \frac{1}{2} \rho V_{\infty}^2 C_{p,\min}
   - \left(P_{vap} - P_{\infty}\right)

and must satisfy:

.. math::

   h(x) > 0

The default values used in this calculation are:

.. list-table:: Cavitation constants
   :header-rows: 1
   :widths: 30 30 40

   * - Quantity
     - Variable
     - Default value
   * - Seawater density
     - ``rho``
     - ``1025.0 kg/m^3``
   * - Atmospheric pressure
     - ``Patm``
     - ``101325.0 Pa``
   * - Vapor pressure
     - ``Pvap``
     - ``3063.7485 Pa``
   * - Gravitational acceleration
     - ``g``
     - ``9.8 m/s^2``
   * - Default ``Cpmin`` if no file is supplied
     - ``Cpmin``
     - ``-1.0``

The cavitation model depends strongly on the quality of the ``Cpmin`` data.

How is pitch stability checked?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pitch stability is checked using a simplified moment balance involving vessel drag, turbine thrust, turbine hub depth, mooring angle, vessel geometry, and pitch hydrostatic stiffness.

The code computes vessel drag as:

.. math::

   F_{vessel} =
   \frac{1}{2} \rho A U_{\text{inf,adjusted}}^2

and turbine thrust as:

.. math::

   F_{turbine,total} = N_t F_t

The total horizontal load used in the pitch check is:

.. math::

   F_{total} = F_{vessel} + F_{turbine,total}

The pitch constraint margin is implemented as:

.. math::

   h(x) =
   K_{\phi} \phi
   - F_{turbine,total} d_{hub}
   - F_{total} X_m \cos(\theta_m)
   - F_{total} Z_m \sin(\theta_m)

where:

- ``Kphi`` is the pitch hydrostatic stiffness.
- ``phi`` is the representative pitch angle.
- ``dHub`` is the hub depth.
- ``Xm`` is the horizontal force-application distance.
- ``Zm`` is the vertical force-application distance.
- ``theta_m`` is the mooring line angle.

The constraint must satisfy:

.. math::

   h(x) > 0

This check is intended as a screening-level constraint and should not replace detailed vessel stability analysis.

Vessel Model
------------

What vessel properties are required for user-defined vessels?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For user-defined vessels, the following keys are expected in ``vessel_properties``:

- ``Xm``
- ``Zm``
- ``Kphi``
- ``theta``
- ``phi``
- ``area``
- ``Cd``

If any of these are missing, ``VesselData`` will raise an error.

What default vessel properties are used?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the vessel is not user-defined, the following default vessel properties are used:

.. list-table:: Default vessel properties
   :header-rows: 1
   :widths: 35 30 35

   * - Quantity
     - Variable
     - Default value
   * - Vessel height
     - ``height``
     - ``0.5 m``
   * - Vessel density
     - ``density``
     - ``500.0 kg/m^3``
   * - Mooring line angle
     - ``theta_m``
     - ``45 deg = 0.7854 rad``
   * - Aspect ratio
     - ``alpha``
     - ``4.0``
   * - Drag coefficient
     - ``Cd``
     - ``0.25``
   * - Pitch angle
     - ``phi``
     - ``10 deg = 0.1745 rad``
   * - Submerged height
     - ``h_s``
     - ``height / 2 = 0.25 m``
   * - Cross-sectional area
     - ``area``
     - ``height * alpha = 2.0 m^2``

Some vessel attributes, such as ``Xm``, ``Zm``, ``Kphi``, and ``VesselVolume``, are not assigned by the default vessel model. These should be supplied explicitly for analyses that require them.

How is vessel drag calculated?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Vessel drag is calculated as:

.. math::

   F_{drag} = \frac{1}{2} \rho C_d A U^2

where:

- ``rho = 1025.0 kg/m^3`` by default.
- ``Cd`` is the vessel drag coefficient.
- ``A`` is the vessel cross-sectional area.
- ``U`` is the adjusted flow speed.

For the default vessel model:

.. math::

   C_d = 0.25

and:

.. math::

   A = 2.0 \; \text{m}^2

LCOE Calculation
----------------

What does the LCOE calculation include?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The LCOE calculation includes:

- CAPEX from the configured cost functions.
- OPEX as a fraction of CAPEX.
- Annual energy production estimated from simulated electrical power.
- Discounted project lifetime.

The result is reported in USD/kWh.

What power signal is used for annual energy in LCOE?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The current LCOE workflow calculates annual energy from ``Pelec``.

For battery-charging studies with power-electronics losses, ``Pbat`` may be a more appropriate delivered-energy metric. Users should review whether ``Pelec`` or ``Pbat`` is appropriate for their analysis.

What LCOE defaults are used by the optimizer?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When using ``LCOEOptimizer.optimize`` without overriding defaults, the following values are used:

.. list-table:: Optimizer LCOE defaults
   :header-rows: 1
   :widths: 35 30 35

   * - Quantity
     - Variable
     - Default value
   * - Customer
     - ``customer``
     - ``"customer_B"``
   * - Application
     - ``application``
     - ``"battery_charging"``
   * - Battery capacity
     - ``BatteryCapacity_kWh``
     - ``10.0 kWh``
   * - Project lifetime
     - ``lifetime``
     - ``10 years``
   * - Discount rate
     - ``discount_rate``
     - ``0.1``
   * - Turbulence intensity
     - ``turbulence_intensity``
     - ``0.0``

These defaults are optimizer defaults only. If users instantiate ``LCOEData`` directly, these values must be provided explicitly.

How is annual energy calculated?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The code integrates the simulated power time series to estimate average power, then scales it to annual energy using:

.. math::

   8760 \; \text{hr/year}

Annual energy is reported in kWh.

Does the capacity factor include all turbines?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The annual energy calculation multiplies instantaneous power by the number of turbines:

.. code-block:: python

   instantaneous_power = Pelec / ((1 + turbulence_intensity) ** 3) * number_of_turbines

Users should ensure that rated power and turbine count are interpreted consistently when comparing capacity factor or system-level power.

How is turbulence intensity used?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The LCOE calculation adjusts instantaneous power by dividing by:

.. math::

   (1 + TI)^3

where ``TI`` is the turbulence intensity input.

The optimizer default is:

.. math::

   TI = 0.0

This is a simplified correction and should be reviewed for the intended application.

How is OPEX calculated?
~~~~~~~~~~~~~~~~~~~~~~~

The current active implementation calculates OPEX as:

.. math::

   OPEX = 0.04 \cdot CAPEX

That is, annual OPEX is assumed to be 4% of total CAPEX.

A SITKANA-specific operating cost function exists in the code, but the currently active ``calculate_total_opex`` method uses the 4% of CAPEX approximation for all customers.

What CAPEX adjustment factors are applied?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After component CAPEX values are summed, an adjustment factor is applied.

.. list-table:: CAPEX adjustment factors
   :header-rows: 1
   :widths: 40 60

   * - Customer
     - Adjustment factor
   * - ``customer_A``
     - ``1.05``
   * - Other customers, including ``customer_B``
     - ``1.0``

What happens if battery capacity is missing?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For ``grid_connection`` applications, battery capacity is internally set to zero.

For non-grid applications, such as ``battery_charging``, battery capacity must be provided and must be greater than zero.

If battery capacity is missing or nonpositive for a non-grid application, the code raises an error.

Cost Models
-----------

Are the cost models general?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

No. The cost models are configuration-dependent and include customer/application-specific assumptions. Users should review ``module_cost_config.py`` and ``module_cost_calculations.py`` before applying results to a new use case.

What cost model configurations are included?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The cost configuration includes two customer keys:

- ``customer_A``
- ``customer_B``

Each customer has:

- ``rotor_and_drivetrain`` cost components.
- ``applications`` cost components for ``grid_connection`` and/or ``battery_charging``.

What battery cost is currently used for SITKANA-style battery charging?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The battery cost function ``calculate_battery_cost_SITKANA`` uses:

.. math::

   \text{battery cost} = 150 \cdot \text{BatteryCapacity}_{kWh}

Thus, the assumed battery cost is:

.. math::

   150 \; \text{USD/kWh}

What currency conversion is used?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following conversion is defined in ``constUnitConvert.py``:

.. math::

   \text{euro2dollar} = 1.26 \cdot 1.1304 = 1.424304

Costs based on kEuro values are converted using:

.. math::

   \text{USD} =
   \text{kEuro}
   \cdot 1000
   \cdot 1.424304

Are permitting costs included?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

No. Permitting costs are not currently included in the LCOE calculation.

See the permitting information page for a qualitative list of agencies and considerations.

Optimization
------------

What optimization method is used?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The current ``LCOEOptimizer`` performs an explicit grid search over user-specified parameter values.

Although older code used ``scipy.optimize.brute``, the current implementation explicitly constructs the grid and evaluates each point.

What defaults are used by the optimizer?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The optimizer defaults are:

.. list-table:: Optimization defaults
   :header-rows: 1
   :widths: 35 30 35

   * - Quantity
     - Variable
     - Default value
   * - Customer
     - ``customer``
     - ``"customer_B"``
   * - Application
     - ``application``
     - ``"battery_charging"``
   * - Battery capacity
     - ``BatteryCapacity_kWh``
     - ``10.0 kWh``
   * - Lifetime
     - ``lifetime``
     - ``10 years``
   * - Discount rate
     - ``discount_rate``
     - ``0.1``
   * - Turbulence intensity
     - ``turbulence_intensity``
     - ``0.0``

What happens when a design violates constraints?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If a design violates any checked constraint, it is assigned a penalty LCOE value of:

.. math::

   10^6

This value is used numerically to exclude infeasible designs from the feasible design table. It is not a physical cost estimate.

Why did optimization fail to find a feasible design?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Common reasons include:

- Hub depth too shallow relative to rotor radius.
- Rated power too low for simulated electrical power.
- Cavitation constraint violation.
- Pitch stability violation.
- Missing or inconsistent turbine configuration parameters.
- Missing vessel properties.
- Battery capacity not provided for battery-charging applications.
- Search bounds too narrow.
- Grid step sizes too coarse.

How are variable bounds interpreted?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The optimizer expects ``variable_bounds`` to map variable names to tuples of:

.. code-block:: python

   (minimum, maximum, step)

The grid values are generated using:

.. code-block:: python

   np.arange(low, high + 0.5 * step, step)

This means the upper bound is usually included if it falls on the step spacing.

Numerical and Software Notes
----------------------------

Does the software validate every physical input?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

No. Some validation is included, but users are responsible for providing physically meaningful inputs, consistent units, and appropriate parameter ranges.

What unit system is used?
~~~~~~~~~~~~~~~~~~~~~~~~~

The software primarily uses SI units:

.. list-table:: Primary unit conventions
   :header-rows: 1
   :widths: 40 60

   * - Quantity
     - Unit
   * - Length
     - m
   * - Time
     - s
   * - Mass
     - kg
   * - Force
     - N
   * - Torque
     - N m
   * - Power
     - W
   * - Energy
     - kWh for annual energy and battery capacity
   * - Cost
     - USD

What useful unit conversions are defined?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following common unit conversions are defined in ``constUnitConvert.py``:

.. list-table:: Unit conversion constants
   :header-rows: 1
   :widths: 35 30 35

   * - Conversion
     - Variable
     - Value
   * - Seconds to days
     - ``sec2days``
     - ``1 / (24 * 3600)``
   * - Miles to meters
     - ``mile2m``
     - ``1609.34``
   * - Meters to kilometers
     - ``m2km``
     - ``1e-3``
   * - Watts to megawatts
     - ``W2MW``
     - ``1e-6``
   * - Watts to kilowatts
     - ``W2kW``
     - ``1e-3``
   * - Kilo-euros to euros
     - ``kE2E``
     - ``1e3``
   * - Newtons to metric tons
     - ``N2mTon``
     - ``1.019716e-4``
   * - Newtons to kilonewtons
     - ``N2kN``
     - ``1e-3``
   * - Euros to dollars
     - ``euro2dollar``
     - ``1.424304``
   * - Feet to meters
     - ``ft2m``
     - ``0.3048``
   * - cm/s to m/s
     - ``cms2ms``
     - ``1e-2``
   * - rad/s to rpm
     - ``rads2rpm``
     - ``60 / (2 pi)``
   * - Cubic meters to cubic centimeters
     - ``m32cm3``
     - ``1e6``
   * - Hours to days
     - ``hrs2days``
     - ``1 / 24``

What should users check before trusting results?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Users should verify:

- Rotor performance data quality.
- Cpmin/cavitation data quality.
- Tidal data source and representativeness.
- Hub depth and mooring depth consistency.
- Vessel geometry and pitch-stiffness assumptions.
- Cost model applicability.
- Battery or grid-connection assumptions.
- Whether power should be evaluated as ``Pelec``, ``Pac``, or ``Pbat`` for the intended use case.
- Whether the default values listed on this page are appropriate for the intended site and design.