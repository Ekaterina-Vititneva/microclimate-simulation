import os
import xarray as xr
import json

# Load the KPI configuration from the JSON file
json_config_path = os.path.join(os.getcwd(), 'config', 'kpi_config.json')

with open(json_config_path, 'r') as f:
    kpi_config = json.load(f)

# Extract KPI options from the JSON config
kpi_options = kpi_config['kpi_options']

def extract_kpis_from_nc(input_path, output_path, kpi_variables):
    print(f"Attempting to open file: {input_path}")
    try:
        # Open the original .nc file
        ds = xr.open_dataset(input_path)
        
        # Filter out KPIs that are not present in the dataset
        available_kpi_variables = [kpi for kpi in kpi_variables if kpi in ds.variables]
        print(f"KPIs to be extracted: {available_kpi_variables}")

        # Check if any KPIs are left to process
        if not available_kpi_variables:
            print("No matching KPIs found in the dataset.")
            return
        
        # Extract only the desired KPIs
        ds_light = ds[available_kpi_variables]
        
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
        print(f"Error processing file {input_path}: {str(e)}")
        raise

# Get the project root directory (one level up from src)
base_dir = os.path.dirname(os.getcwd())

# Define the status quo and optimized directories
statusquo_dir = os.path.join(base_dir, 'data', 'statusquo')
optimized_dir = os.path.join(base_dir, 'data', 'opti')

input_file = 'Playground_2024-07-06_04.00.00'
extension = '.nc'

# Relative paths to files
input_file_statusquo = os.path.join(statusquo_dir, input_file + extension)
input_file_optimized = os.path.join(optimized_dir, input_file + extension)

# Fix the output file path construction
output_file_statusquo = os.path.join(statusquo_dir, input_file + "_light" + extension)
output_file_optimized = os.path.join(optimized_dir, input_file + "_light" + extension)

# Run the extraction for the status quo dataset
print("Processing status quo file...")
extract_kpis_from_nc(input_file_statusquo, output_file_statusquo, kpi_options)

# Run the extraction for the optimized dataset
print("Processing optimized file...")
extract_kpis_from_nc(input_file_optimized, output_file_optimized, kpi_options)