from flask import Flask, request, send_file, render_template
import pandas as pd
import numpy as np
import io

app = Flask(__name__)

# Constants
n_air = 1.0  # Refractive index of air

# Function to calculate n and k based on equations
def calculate_n_k(wavelength, transmittance, reflectance):
    # Convert transmittance and reflectance from percentage to fraction
    R = reflectance / 100
    T = transmittance / 100

    # Validate the input values to avoid invalid calculations
    if R <= 0 or R >= 1 or T <= 0 or T >= 1:
        return np.nan, np.nan

    # Calculate n using reflectance equation
    try:
        n = np.sqrt((1 + R) / (1 - R))
    except ValueError:
        n = np.nan

    # Calculate k using transmittance equation
    try:
        k = np.sqrt(((4 * n_air * n * T) / ((n_air + n)**2)) - T**2)
    except ValueError:
        k = np.nan

    return n, k


# Route to handle file upload and n, k extraction
@app.route('/convert_TR', methods=['GET'])
def main():
    return render_template('convert_TR.html');
# Route to handle file upload and n, k extraction
@app.route('/convert_TR', methods=['POST'])
def convert_transmittance_reflectance():
    file = request.files.get('file')
    if not file:
        return "No file uploaded", 400

    # Read the CSV file
    try:
        df = pd.read_csv(file)
    except Exception as e:
        return f"Error reading CSV file: {str(e)}", 400

    # Validate required columns
    required_columns = {'wavelength', 'transmittance', 'reflectance'}
    if not required_columns.issubset(df.columns.str.lower()):
        return "CSV file must contain 'wavelength', 'transmittance', and 'reflectance' columns", 400

    # Ensure column names are lowercase
    df.columns = df.columns.str.lower()

    # Initialize lists for n and k values
    n_values = []
    k_values = []

    # Calculate n and k for each row
    for _, row in df.iterrows():
        wavelength = row['wavelength']
        transmittance = row['transmittance']
        reflectance = row['reflectance']

        # Calculate n and k
        n, k = calculate_n_k(wavelength, transmittance, reflectance)
        n_values.append(n)
        k_values.append(k)

    # Create a new DataFrame with the results
    result_df = pd.DataFrame({
        'wavelength': df['wavelength'],
        'n': n_values,
        'k': k_values
    })

    # Save the result to a CSV file in memory
    output = io.BytesIO()
    result_df.to_csv(output, index=False)
    output.seek(0)

    # Return the CSV file as a download
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name='nk_results.csv'
    )

if __name__ == '__main__':
    app.run(debug=True)