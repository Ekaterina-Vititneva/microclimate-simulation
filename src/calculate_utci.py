import xarray as xr
import numpy as np
from utci_calculator import extract_and_calculate_utci
import os

# Function to add UTCI to a dataset
def add_utci_to_dataset(ds):
    utci_values = []
    for t in range(len(ds['Time'])):
        print(f"Calculating UTCI for time index {t}")
        utci = extract_and_calculate_utci(ds, t)
        
        # Check the shape of utci
        print(f"Original shape of UTCI at time index {t}: {utci.shape}")
        
        # Ensure it is 2D by selecting the appropriate slice if needed
        if len(utci.shape) > 2:
            utci = utci[0]  # Select the first slice if there's an extra dimension
            print(f"Adjusted shape of UTCI at time index {t}: {utci.shape}")
        
        utci_values.append(utci)
    
    # Convert list of 2D arrays into a 3D array
    utci_array = xr.DataArray(
        data=np.array(utci_values),  # Should have shape (Time, GridsJ, GridsI)
        dims=('Time', 'GridsJ', 'GridsI'),
        coords={'Time': ds['Time'], 'GridsJ': ds['GridsJ'], 'GridsI': ds['GridsI']},
        name='UTCI'
    )
    
    # Add UTCI to the dataset
    ds['UTCI'] = utci_array
    return ds

# Paths to your data files
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

statusquo_file_path = os.path.join(base_dir, 'data', 'statusquo', 'Playground_2024-07-06_04.00.00_light.nc')
optimized_file_path = os.path.join(base_dir, 'data', 'opti', 'Playground_2024-07-06_04.00.00_light.nc')

# Load datasets
ds_statusquo = xr.open_dataset(statusquo_file_path)
ds_optimized = xr.open_dataset(optimized_file_path)

# Add UTCI to the datasets
ds_statusquo = add_utci_to_dataset(ds_statusquo)
ds_optimized = add_utci_to_dataset(ds_optimized)

"""
# Save the updated datasets
ds_statusquo.to_netcdf(statusquo_file_path)
ds_optimized.to_netcdf(optimized_file_path)
"""
ds_statusquo.to_netcdf(os.path.join(base_dir, 'data', 'statusquo', 'Playground_2024-07-06_04.00.00_light_updated.nc'))
ds_optimized.to_netcdf(os.path.join(base_dir, 'data', 'opti', 'Playground_2024-07-06_04.00.00_light_updated.nc'))
#"""

print("UTCI calculation and dataset saving completed successfully.")