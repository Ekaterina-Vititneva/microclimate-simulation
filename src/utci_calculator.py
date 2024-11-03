import numpy as np
from pythermalcomfort.models import utci

def extract_kpi_data(ds, kpi_name, time_index):
    """
    Extracts data for a specific KPI from the dataset at a given time index.
    """
    return ds[kpi_name].isel(Time=time_index).values

def calculate_utci(air_temp, wind_speed, rel_humidity, mrt):
    """
    Calculate the UTCI using the provided environmental parameters.
    :param air_temp: Air temperature in °C
    :param wind_speed: Wind speed in m/s
    :param rel_humidity: Relative humidity in %
    :param mrt: Mean radiant temperature in °C
    :return: Calculated UTCI values
    """
    try:
        return utci(tdb=air_temp, v=wind_speed, rh=rel_humidity, tr=mrt)
    except TypeError as e:
        print(f"Error calculating UTCI: {e}")
        return None

def extract_and_calculate_utci(ds, time_index):
    """
    Extracts required data and calculates UTCI.
    """
    air_temp = extract_kpi_data(ds, 'T', time_index)
    wind_speed = extract_kpi_data(ds, 'WindSpd', time_index)
    rel_humidity = extract_kpi_data(ds, 'RelHum', time_index)
    mrt = extract_kpi_data(ds, 'TMRT', time_index)
    
    utci = calculate_utci(air_temp, wind_speed, rel_humidity, mrt)
    return utci
