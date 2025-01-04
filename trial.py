import yaml
import numpy as np
yml_file_path = "C:/Users/adapt/OneDrive/Documents/Matlab_py/refractiveindex.info-database-master/database/data-nk/main/TiO2/Sarkar.yml"

def load_material_data_from_yaml(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)

    # Extract wavelength, n, and k values
    wavelengths = []
    n_values = []
    k_values = []
    
    for entry in data['DATA'][0]['data'].strip().split('\n'):
        try:
            wavelength, n, k = map(float, entry.split())
            wavelengths.append(wavelength)
            n_values.append(n)
            k_values.append(k)
        except ValueError:
            print(f"Skipping invalid entry in {file_path}: {entry}")

    return {
        'wavelength': np.array(wavelengths),
        'n': np.array(n_values),
        'k': np.array(k_values)
    }
