import xarray as xr

def extract_kpis_from_nc(input_path, output_path, kpi_variables):
    # Open the original .nc file
    ds = xr.open_dataset(input_path)
    
    # Extract only the desired KPIs
    ds_light = ds[kpi_variables]
    
    # Save the lighter version of the dataset
    ds_light.to_netcdf(output_path)
    
    print(f"Light version of dataset saved to {output_path}")

# File paths
input_file = "data/statusquo/Playground_2024-07-06_04.00.00.nc"
output_file = "data/statusquo/Playground_light.nc"

# The KPIs to keep
kpis = ['TSurf']

# Run the extraction
extract_kpis_from_nc(input_file, output_file, kpis)
