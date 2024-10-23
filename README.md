# microclimate-simulation

## Goal

The goal of this project is to develop Python scripts that generate clear, insightful visualizations
of these data outputs. These visualizations should enable users to easily interpret
the results, compare the two scenarios, and gain a comprehensive understanding
of how the mitigation measures affect thermal comfort.

The final output should present the visualizations in a report-style format,
ensuring that the graphics effectively communicate the differences between the
scenarios including some short information about what and why it is shown.

**The provided data contains:**

- The input data of both simulation runs
  - model area (INX-File)
  - simulation config (SIMX-File)
  - project information (INFOX-File and EDB-File)
  - climate input data (FOX-File)
- The output data of both simulation runs
  - netCDF file format

## File extensions

### INX-File

_Model Area File_

**Purpose:** This file defines the model area for the simulation. It specifies the grid layout, such as the number of cells, size of each grid cell, and boundary conditions.

**Contents:**
Spatial details of the area being modeled.
Grid structure (3D representation of the environment).

**How to Use:** When visualizing the data, this file helps in mapping the results (e.g., temperature distribution) to a specific geographical region or grid.

- rasterized ENVI-met INX file.
- Generate the surface input files (.INX) to run the simulation.
- https://envi-met.com/microclimate-simulation-software/

### SIMX-File

_Simulation configuration files_

**Purpose:** This file contains the configuration settings for the simulation, such as simulation start time, duration, and various physical parameters (e.g., heat fluxes, vegetation parameters).

**Contents:**
Simulation start and end times.
Physical parameters (such as roughness, heat transfer coefficients, etc.).

**How to Use:** The settings within this file help you understand the context of the simulation, which is essential when interpreting the results. It’s important to know these parameters to properly compare the two scenarios.

### INFOX-File

_Project Information File_

**Purpose:** This file holds metadata about the project, such as project name, author, and description.

**Contents:**
General project information (descriptions, versioning, etc.).

**How to Use:** This file doesn’t usually have direct implications on the simulation data but is useful for tracking and documenting the project. It can be included in the report for context.

### EDB-File

_ENVI-met Database File_

**Purpose:** Contains specific information about materials and vegetation used in the model (like albedo, thermal properties, etc.). This is key for modeling interactions between the environment and climate.

**Contents:**
Materials data (building materials, surface properties).
Vegetation data (type, size, transpiration rates).

**How to Use:** When interpreting thermal comfort or environmental conditions, the material and vegetation properties play a major role in how heat and moisture are exchanged in the model.

### FOX-File

_Climate Input Data File_

**Purpose:** This file provides climate input data for the simulation, such as temperature, wind speed, solar radiation, and humidity.

**Contents:**
Climate conditions over time (hourly or finer time steps).

**How to Use:** These inputs drive the simulation and define the external environmental conditions. When comparing scenarios, differences in the climate data may need to be accounted for.

### netCDF

_Main output data, used for generating visualizations._

**Purpose:** netCDF (Network Common Data Form) is a widely-used format for storing multidimensional data, such as temperature, wind, and humidity, over a defined grid and time series. The netCDF files store the simulation output for both the status quo and optimized scenarios.

**Contents:**
Variables like temperature, humidity, wind, and more.
3D arrays corresponding to values at different grid points and time steps.

**How to Use:** You'll use Python libraries (e.g., xarray, netCDF4) to extract and visualize the data. For example, you can generate heatmaps of temperature distribution, compare wind speeds at different heights, or calculate thermal comfort indices based on temperature and humidity.

</details>

## Set up

### Running locally

1. Activate the venv

```
.\venv\Scripts\activate
```

```
pip install -r requirements-dev.txt
```
