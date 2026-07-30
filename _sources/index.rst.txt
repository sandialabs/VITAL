VITAL
=====

The **Vessel Integrated Turbine Assessment for LCOE (VITAL)** is an open-source software package developed to support screening-level assessment of tidal energy systems integrated with vessels, floating platforms, or other deployable marine-energy infrastructure.

VITAL combines tidal resource data, rotor performance information, vessel or platform assumptions, dynamic simulation, physical constraint checks, cost models, annual energy production, and Levelized Cost of Energy (LCOE) calculations.

The software supports representative workflows for battery-charging and grid-connected tidal energy applications. Results are intended for early-stage comparison of candidate sites and design assumptions, not final engineering, permitting, or deployment decisions.

Getting Started
---------------

To get started, see the installation instructions in the `GitHub repository`_. New users are encouraged to begin with the Quickstart tutorial and then review the module tutorials as needed.

Application-focused case studies are provided to demonstrate representative battery-charging and grid-connected workflows.

Development Team
----------------

VITAL is developed by `Sandia National Laboratories`_, with funding support from the U.S. Department of Energy (DOE) Office of Technology Transitions (OTT) and the DOE Water Power Technologies Office (WPTO).

This project is funded through the DOE Technology Commercialization Fund (TCF) Base Annual Appropriations Core Laboratory Infrastructure for Market Readiness (CLIMR).

Sandia National Laboratories is a multi-mission laboratory managed and operated by National Technology and Engineering Solutions of Sandia, LLC., a wholly owned subsidiary of Honeywell International, Inc., for the U.S. Department of Energy's National Nuclear Security Administration under contract DE-NA0003525.

.. _GitHub repository: https://github.com/sandialabs/VITAL
.. _Sandia National Laboratories: https://www.sandia.gov

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Documentation

   overview
   constraint
   assumptions_and_faq

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Getting Started

   examples/01_quickstart.ipynb

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Module Tutorials

   examples/02_tidaldata.ipynb
   examples/03_rotordata.ipynb
   examples/04_rotor_simulation.ipynb
   examples/05_constraint_checking.ipynb
   examples/06_lcoe_calculation.ipynb
   examples/07_optimization.ipynb
   examples/08_loss_models.ipynb

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Case Studies

   examples/sitkana_battery_charging.ipynb
   examples/hdps_grid_connection.ipynb

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: API Documentation

   api_docs/vital

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Additional Resources

   permitting_info