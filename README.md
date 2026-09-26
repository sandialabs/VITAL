# VITAL: Vessel Integrated Turbine Assessment for LCOE

VITAL is an open-source Python package for screening-level assessment of tidal energy systems integrated with vessels, floating platforms, or other deployable marine-energy infrastructure.

VITAL combines tidal resource data, rotor performance information, vessel or platform assumptions, rotor simulation, physical constraint checks, cost modeling, annual energy production, and Levelized Cost of Energy (LCOE) calculations.

VITAL can be used for:

- battery-charging tidal energy applications,
- grid-connected tidal energy applications,
- design-variable optimization,
- comparison of candidate sites and system assumptions,
- and export of key results for review and archival.

Results are intended for early-stage screening and comparison. They should not be interpreted as final engineering, permitting, or deployment recommendations.

## Documentation

Full documentation is available at:

<https://sandialabs.github.io/VITAL/>

The documentation includes tutorials, case studies, API documentation, assumptions, input-format guidance, and reporting guidance.

## Installation

VITAL uses Conda to manage its Python environment.

If you do not already have Conda installed, install one of the following:

- Anaconda: <https://www.anaconda.com/download>
- Miniconda: <https://docs.conda.io/en/latest/miniconda.html>

### 1. Clone the repository

Open a terminal and run:

```bash
git clone https://github.com/sandialabs/VITAL.git
cd VITAL
```

### 2. Create the Conda environment

```bash
conda env create --file environment.yml
```

### 3. Activate the environment

```bash
conda activate VITAL_env
```

### 4. Install VITAL

```bash
pip install -e .
```

For development or documentation work, install the optional development tools:

```bash
pip install -e ".[dev]"
```

## Running the examples

After installation, start JupyterLab:

```bash
jupyter lab
```

or Jupyter Notebook:

```bash
jupyter notebook
```

Then open the notebooks in the `example/` directory.

A good starting point is:

```text
example/01_quickstart.ipynb
```

The example notebooks are organized as:

```text
example/
├── 01_quickstart.ipynb
├── 02_tidaldata.ipynb
├── 03_rotordata.ipynb
├── 04_rotor_simulation.ipynb
├── 05_constraint_checking.ipynb
├── 06_lcoe_calculation.ipynb
├── 07_optimization.ipynb
├── 08_loss_models.ipynb
├── sitkana_battery_charging.ipynb
└── hdps_grid_connection.ipynb
```

New users should begin with `01_quickstart.ipynb` before moving to the module tutorials or case studies.

## Reporting

VITAL can export LCOE and optimization results to Markdown and CSV files. These reports are intended for review, sharing, and archival of screening-level results.

See the documentation for details on expected input formats, engineering units, and exported report files.

## Building the documentation locally

To build the documentation on your machine, activate the VITAL environment and move into the `docs` folder:

```bash
conda activate VITAL_env
cd docs
```

On macOS or Linux, run:

```bash
make clean
make html
```

On Windows, run:

```bat
make.bat clean
make.bat html
```

The built documentation will be available at:

```text
docs/build/index.html
```

Open that file in a web browser.

## Managing the Conda environment

To deactivate the environment:

```bash
conda deactivate
```

To remove the environment:

```bash
conda env remove --name VITAL_env
```

## License

Copyright 2025 National Technology & Engineering Solutions of Sandia, LLC (NTESS).

Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains certain rights in this software.

This project is licensed under the Apache License, Version 2.0. See `LICENSE.md` for details.

Third-party license notices are provided in the `LICENSE/` directory.