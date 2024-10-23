import os
import requests
import xarray as xr
from dask.diagnostics import ProgressBar

# Dropbox direct download link with ?dl=1 for direct download
dropbox_url = "https://www.dropbox.com/scl/fi/rh1ut0xug2cs0obkbyw1x/Playground_2024-07-06_04.00.00.nc?dl=1"

# Define chunk size (1 MB per chunk)
chunk_size = 1024 * 1024  # 1 MB

# Path to save the file
nc_file_path = "data/statusquo/Playground_2024-07-06_04.00.00.nc"

# Stream download and save the file in chunks
def download_file_in_chunks(url, dest_path, chunk_size):
    with requests.get(url, stream=True) as response:
        response.raise_for_status()  # Check for request errors
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:  # filter out keep-alive chunks
                    f.write(chunk)
            print(f"File downloaded successfully to {dest_path}")
    file_size = os.path.getsize(dest_path)
    print(f"Downloaded file size: {file_size} bytes")

# Download the file in chunks if it doesn't already exist
if not os.path.exists(nc_file_path):
    download_file_in_chunks(dropbox_url, nc_file_path, chunk_size)

# Load the netCDF file using Xarray and Dask for chunked processing
def load_nc_file(file_path):
    try:
        # Use Dask for lazy loading and chunking
        ds = xr.open_dataset(file_path, engine='netcdf4', chunks={'Time': 10})
        return ds
    except Exception as e:
        print(f"Error opening file {file_path}: {e}")
        return None

ds = load_nc_file(nc_file_path)

# Check if the dataset was loaded successfully
if ds is not None:
    print(f"Dataset loaded with dimensions: {ds.dims}")
else:
    print("Failed to load the NetCDF file.")

# Visualize and process in chunks using Dask
if ds is not None:
    with ProgressBar():
        surface_temperature = ds['TSurf'].mean(dim='Time').compute()  # Example computation
        print(surface_temperature)
