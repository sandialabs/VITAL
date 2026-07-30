# VITAL: Vessel Integrated Turbine Assessment for LCOE

VITAL is an open-source Python package for screening-level assessment of tidal energy systems integrated with vessels, floating platforms, or other deployable marine-energy infrastructure.

The software combines tidal resource data, rotor performance information, vessel or platform assumptions, dynamic rotor simulation, physical constraint checks, cost models, annual energy production, and Levelized Cost of Energy (LCOE) calculations.

VITAL supports representative workflows for:

- battery-charging applications,
- grid-connected applications,
- design-variable grid-search optimization,
- and early-stage comparison of candidate sites and system assumptions.

Results are intended for early-stage screening and comparison. They should not be interpreted as final engineering, permitting, or deployment recommendations.

## Documentation

The documentation is available at:

<https://sandialabs.github.io/VITAL/>

The documentation includes:

- a quickstart tutorial,
- module-specific tutorials,
- case studies,
- assumptions and FAQ,
- and API documentation.

## Prerequisites

Install Conda or Miniconda before creating the VITAL environment.

- Anaconda: <https://www.anaconda.com/download>
- Miniconda: <https://docs.conda.io/en/latest/miniconda.html>

These instructions are intended for macOS, Windows, and Linux users. Commands should be run from a terminal:

- macOS/Linux: Terminal
- Windows: Anaconda Prompt, Miniconda Prompt, PowerShell, or Windows Terminal

For users new to Conda, the Anaconda and Miniconda documentation provide installation and getting-started resources.

## New to command-line tools?

Most installation steps are run from a terminal.

- On **macOS**, open the **Terminal** app.
- On **Windows**, open **Anaconda Prompt** or **Miniconda Prompt** after installing Conda.
- On **Linux**, open your usual terminal application.

A few tips:

- Type or paste one command at a time, then press **Enter**.
- Run commands from the VITAL repository folder after cloning the repository.
- If a command starts with `cd`, it changes the current folder.
- If you close and reopen your terminal, activate the environment again with:

```bash
conda activate VITAL_env
```

If you are unsure where you are in the terminal, run:

```bash
pwd
```

on macOS/Linux, or:

```bat
cd
```

on Windows.

## Installation

### 1. Clone the repository

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

### 4. Install VITAL in editable mode

```bash
pip install -e .
```

For development and documentation dependencies, use:

```bash
pip install -e ".[dev]"
```

## Running the tutorials

After installing VITAL, launch Jupyter Notebook or JupyterLab:

```bash
jupyter notebook
```

or:

```bash
jupyter lab
```

Then open the notebooks in the `example/` directory.

Recommended learning path:

1. `01_quickstart.ipynb`
2. `02_tidaldata.ipynb`
3. `03_rotordata.ipynb`
4. `04_rotor_simulation.ipynb`
5. `05_constraint_checking.ipynb`
6. `06_lcoe_calculation.ipynb`
7. `07_optimization.ipynb`
8. `08_loss_models.ipynb`

Case studies are also provided in the `example/` directory.

## Building the documentation locally

From the repository root, activate the environment and move into the documentation folder:

```bash
conda activate VITAL_env
cd docs
```

### macOS/Linux

```bash
make clean
make html
```

### Windows

```bat
make.bat clean
make.bat html
```

The built documentation will be available at:

```text
docs/build/index.html
```

Open that file in a web browser.

On macOS, you can open it from the `docs` directory with:

```bash
open build/index.html
```

On Windows, you can open it from File Explorer or run from the `docs` directory:

```bat
start build\index.html
```

On Linux, you can open it from a file browser or run from the `docs` directory:

```bash
xdg-open build/index.html
```

## Managing the Conda environment

Deactivate the environment:

```bash
conda deactivate
```

Remove the environment:

```bash
conda env remove --name VITAL_env
```

## License

Copyright 2025 National Technology & Engineering Solutions of Sandia, LLC (NTESS).

Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains certain rights in this software.

This project is licensed under the Apache License, Version 2.0. See `LICENSE.md` for details.

Third-party license notices are provided in the `LICENSE/` directory.