# microclimate-simulation

![Surface Temperature plot (TSurf)](assets/TSurf_output_statusquo.png)

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

![Dashboard](assets/dashboard.png)

## Set up

### Running locally

1. Activate the venv

```
.\venv\Scripts\activate
```

```
pip install -r requirements-dev.txt
```

## Details

- [File extensions](data/file_extensions.md)
- [KPIs description (assumptions)](notebooks/kpis_description.md)
