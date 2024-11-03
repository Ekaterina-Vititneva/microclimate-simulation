# utci_calculator.py
import numpy as np
from pythermalcomfort.models import utci

def extract_kpi_data(ds, kpi_name):
    """
    Extracts 3D data for a specific KPI from the dataset without slicing.
    """
    return ds[kpi_name].values  # Keep the full 3D data

def calculate_utci(air_temp, wind_speed, rel_humidity, mrt):
    """
    Calculate the UTCI using the provided environmental parameters.
    :param air_temp: 3D array of air temperature in °C
    :param wind_speed: 3D array of wind speed in m/s
    :param rel_humidity: 3D array of relative humidity in %
    :param mrt: 3D array of mean radiant temperature in °C
    :return: 3D array of calculated UTCI values
    """
    try:
        utci_result = np.vectorize(utci)(tdb=air_temp, v=wind_speed, rh=rel_humidity, tr=mrt)
        return utci_result
    except TypeError as e:
        print(f"Error calculating UTCI: {e}")
        return None

def extract_and_calculate_utci(ds, time_index):
    """
    Extracts required data and calculates UTCI for a given time index without reducing dimensionality.
    """
    air_temp = extract_kpi_data(ds, 'T')[time_index]
    wind_speed = extract_kpi_data(ds, 'WindSpd')[time_index]
    rel_humidity = extract_kpi_data(ds, 'RelHum')[time_index]
    mrt = extract_kpi_data(ds, 'TMRT')[time_index]

    # Check for any missing values in the input data
    if np.isnan(air_temp).any() or np.isnan(wind_speed).any() or np.isnan(rel_humidity).any() or np.isnan(mrt).any():
        print(f"Warning: Missing data found at time index {time_index}")
        # Optional: Replace NaNs or handle this case appropriately

    # Calculate UTCI
    utci_result = calculate_utci(air_temp, wind_speed, rel_humidity, mrt)
    return utci_result