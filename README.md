# microclimate-simulation

![Surface Temperature plot (TSurf)](assets/TSurf_output_statusquo.png)

## Goal

Visualization of ENVI-met microclimate simulation data.

This project is based on two simulation outputs from the ENVI-met microclimate
model, each representing different scenarios. The first scenario illustrates the
current or "status quo" conditions, while the second scenario (optimized) includes
various mitigation measures aimed at optimizing thermal comfort in the area.

The goal of this project is to develop Python scripts that generate clear, insightful visualizations
of these data outputs. These visualizations enable users to easily interpret
the results, compare the two scenarios, and gain a comprehensive understanding
of how the mitigation measures affect thermal comfort.

**The input data contains:**

- The input data of both simulation runs
  - model area (INX-File)
  - simulation config (SIMX-File)
  - project information (INFOX-File and EDB-File)
  - climate input data (FOX-File)
- The output data of both simulation runs
  - netCDF file format

## Demo

[Microclimate Simulation Dashboard](https://microclimate-simulation.onrender.com/)
![Dashboard](assets/dashboard.png)

## Details

- [More info about the example](https://envi-met.info/doku.php?id=examples:playground)
- [KPIs description](https://envi-met.info/doku.php?id=filereference:output:atmosphere)
- [ENVI-met Model Architecture](https://envi-met.info/doku.php?id=intro:modelconept)
- [File extensions](data/file_extensions.md)

![The Playground model](https://envi-met.info/lib/exe/fetch.php?w=800&tok=812d4d&media=examples:2024-09-13_21h01_27.png)

## Set up

### Running locally

1. Activate the venv

```
.\venv\Scripts\activate
```

2. Intall the dependencies

```
pip install -r requirements.txt
```

3. Naviagate to /src folder

```
cd src
```

4. Naviagate to /src folder

```
python app.py
```

---

To print the repositiry structure in terminal:

```
Get-ChildItem -Recurse -File | Where-Object { $_.FullName -notmatch "venv|__pycache__" } | Format-Table -Property FullName
```
