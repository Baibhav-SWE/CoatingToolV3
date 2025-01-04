import os
import yaml
import pandas as pd

# Define input and output directories
input_directory = r"C:\Users\adapt\OneDrive\Documents\Matlab_py\refractiveindex.info-database-master\database\data-nk\main"  # Path to the main directory with subfolders of YAML files
output_directory = r"C:\Users\adapt\OneDrive\Documents\Matlab_py\output_csv_files"  # Path to output CSV files

# Create output directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

def yaml_to_csv(yaml_path, csv_path):
    try:
        with open(yaml_path, 'r', encoding='utf-8') as file:  # Specify encoding
            data = yaml.safe_load(file)
    except (yaml.YAMLError, UnicodeDecodeError) as e:
        print(f"Error reading YAML file {yaml_path}: {e}")
        return  # Skip this file

    # Check if 'DATA' key exists and has 'data' as expected format
    if 'DATA' in data and 'data' in data['DATA'][0]:
        # Extract and parse data, allowing for both two-value and three-value lines
        rows = []
        for line in data['DATA'][0]['data'].strip().split('\n'):
            try:
                parts = list(map(float, line.split()))
                if len(parts) == 3:
                    wavelength, n, k = parts  # Normal three-value line
                elif len(parts) == 2:
                    wavelength, n = parts  # Only two values, set k to 0
                    k = 0
                else:
                    print(f"Skipping invalid line in {yaml_path}: {line}")
                    continue
                rows.append([int(wavelength * 1000), n, k])  # Convert wavelength to nm and round to integer
            except ValueError:
                print(f"Skipping invalid line in {yaml_path}: {line}")

        # Convert to DataFrame
        df = pd.DataFrame(rows)
        # Save to CSV without headers
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)  # Ensure directory exists
        df.to_csv(csv_path, index=False, header=False)
        print(f"Converted {yaml_path} to {csv_path}")
    else:
        print(f"Skipping {yaml_path}: 'DATA' or 'data' structure not found")

# Traverse the input directory recursively to process each .yaml file
for root, dirs, files in os.walk(input_directory):
    for filename in files:
        if filename.endswith('.yml') or filename.endswith('.yaml'):
            yaml_path = os.path.join(root, filename)
            # Maintain the folder structure in the output directory
            relative_path = os.path.relpath(yaml_path, input_directory)
            csv_filename = os.path.splitext(relative_path)[0] + '.csv'
            csv_path = os.path.join(output_directory, csv_filename)
            
            # Convert YAML to CSV
            yaml_to_csv(yaml_path, csv_path)
