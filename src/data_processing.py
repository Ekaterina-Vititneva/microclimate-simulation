import os
import xarray as xr

def extract_kpis_from_nc(input_path, output_path, kpi_variables):
    print(f"Attempting to open file: {input_path}")
    try:
        # Open the original .nc file
        ds = xr.open_dataset(input_path)
        
        # Extract only the desired KPIs
        ds_light = ds[kpi_variables]
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Check if the output file already exists, and delete it if so
        if os.path.exists(output_path):
            os.remove(output_path)
            print(f"Existing file {output_path} removed.")
        
        # Save the lighter version of the dataset
        ds_light.to_netcdf(output_path)
        
        # Explicitly close the dataset to free resources
        ds_light.close()
        print(f"Light version of dataset saved to {output_path}")
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        raise

# Get the project root directory (one level up from src)
base_dir = os.path.dirname(os.getcwd())
#print(f"Project root directory: {base_dir}")

# Define the status quo and optimized directories
statusquo_dir = os.path.join(base_dir, 'data', 'statusquo')
optimized_dir = os.path.join(base_dir, 'data', 'opti')

input_file = 'Playground_2024-07-06_04.00.00'
extension = '.nc'

# Relative paths to files
input_file_statusquo = os.path.join(statusquo_dir, input_file + extension)
input_file_optimized = os.path.join(optimized_dir, input_file + extension)
#print(f"Input file path: {input_file_statusquo}")
#print(f"File exists: {os.path.exists(input_file_statusquo)}")

# Fix the output file path construction
output_file_statusquo = os.path.join(statusquo_dir, input_file + "_light" + extension)
output_file_optimized = os.path.join(optimized_dir, input_file + "_light" + extension)

# The KPIs to keep
kpis = ['TSurf', 'AirTempAtVeg', 'Albedo']

# Run the extraction
extract_kpis_from_nc(input_file_statusquo, output_file_statusquo, kpis)
#extract_kpis_from_nc(input_file_optimized, output_file_optimized, kpis)