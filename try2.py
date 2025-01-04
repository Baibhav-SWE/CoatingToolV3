import os
from collections import defaultdict
import yaml


# Path to the main directory where your folders are located
yml_file_path = "C:/Users/adapt/OneDrive/Documents/Matlab_py/refractiveindex.info-database-master/database/data-nk/main/TiO2/Sarkar.yml"


# Function to parse the DATA field
def parse_data_section(data_section):
    # Initialize lists for wavelength, n, and k
    wavelengths = []
    ns = []
    ks = []

    # Check if 'data' key is present in the DATA section
    if 'data' in data_section[0]:
        # Split the data string by lines
        lines = data_section[0]['data'].strip().split('\n')
        
        # Process each line
        for line in lines:
            # Split each line by whitespace, assuming it's in "wavelength n k" format
            try:
                # Extract wavelength, n, and k values from each line
                wavelength, n, k = map(float, line.split())
                wavelengths.append(wavelength)
                ns.append(n)
                ks.append(k)
            except ValueError:
                # Skip lines that don't match the expected numerical format
                pass

    return wavelengths, ns, ks

# Load the YAML file
with open(yml_file_path, 'r') as file:
    data = yaml.safe_load(file)

# Extract and parse the DATA section if it exists
if 'DATA' in data:
    wavelengths, ns, ks = parse_data_section(data['DATA'])
    
    if wavelengths and ns and ks:
        # Print the parsed values
        print("Wavelength:", wavelengths)
        print("n:", ns)
        print("k:", ks)
    else:
        print("No valid data found in the 'DATA' section.")
else:
    print("DATA section not found in the file.")
