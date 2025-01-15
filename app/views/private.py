from flask import (
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    session,
)
import numpy as np
import os
from set_stack import set_stack
from ATR1D import ATR1D
from get_electric import get_electric
from random import randint
from scipy.optimize import differential_evolution
from color_chart import plot_color_chart
from email.mime.text import MIMEText
from shopify_webhooks.routes import shopify_bp
from app.utils.database import init_db, get_db, get_users_collection
from app.decorators import login_required, subscription_required

# Temporary storage for OTPs (use a database or Redis in production)
otp_storage = {}

# Directory containing CSV material files
materials_directory = r"C:\Coatingtool\output_csv_files"
UPLOAD_FOLDER = r"C:\Coatingtool\output_csv_files"
UPLOADS_DIRECTORY = os.path.join(
    UPLOAD_FOLDER, "uploads"
)  # Path for user-uploaded files
GLS_FILE_PATH = r"C:\Coatingtool\GLS_NEW.csv"

# Ensure both the main upload directory and the uploads subfolder exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(UPLOADS_DIRECTORY, exist_ok=True)


def index():
    if not session.get("logged_in"):
        return redirect(url_for("app.frontpage"))

    # Retrieve inputs from the session
    start_wavelength = session.get("start_wavelength", 380)
    end_wavelength = session.get("end_wavelength", 1080)
    glass_thickness = session.get("glass_thickness", 320000)
    theta = session.get("theta", 0)
    incoh = session.get("incoh", 1000)

    return render_template(
        "private/index.html",
        first_name=session.get("first_name"),
        start_wavelength=start_wavelength,
        end_wavelength=end_wavelength,
        glass_thickness=glass_thickness,
        theta=theta,
        incoh=incoh,
    )


@login_required
def welcome():
    if request.method == "POST":
        # Get the data from the form submission
        start_wavelength = int(request.form["start_wavelength"])
        end_wavelength = int(request.form["end_wavelength"])
        glass_thickness = int(request.form["glass_thickness"])
        theta = float(request.form["theta"])
        incoh = float(request.form["incoh"])

        # Store these inputs in the session
        session["start_wavelength"] = start_wavelength
        session["end_wavelength"] = end_wavelength
        session["glass_thickness"] = glass_thickness
        session["theta"] = theta
        session["incoh"] = incoh

        return redirect(url_for("app.index"))

    print("Session data in welcome route:", session)  # Debugging: Print session data
    return render_template("private/welcome.html", first_name=session.get("first_name"))


@login_required
def help():
    return render_template("private/help.html", first_name=session.get("first_name"))


@login_required
def materials():
    # Fetch the list of available materials from the directory or database
    materials_list = os.listdir(
        materials_directory
    )  # Assuming materials are stored as files
    return render_template(
        "private/available_materials.html",
        materials=materials_list,
        first_name=session.get("first_name"),
    )


def get_materials():
    materials = {}
    for root, dirs, files in os.walk(materials_directory):
        for file in files:
            if file.endswith(".csv"):
                folder_name = os.path.basename(root)
                if folder_name not in materials:
                    materials[folder_name] = []
                materials[folder_name].append(file)
    return jsonify(materials)


def preview_material():
    folder = request.args.get("folder")
    material = request.args.get("material")

    if folder and material:
        # Construct path using folder and material
        material_path = os.path.join(materials_directory, folder, material)
    else:
        # Use filename directly if no folder is provided
        filename = request.args.get("filename")
        material_path = os.path.join(materials_directory, filename)

    try:
        with open(material_path, "r") as file:
            lines = [file.readline().strip() for _ in range(10)]
        return jsonify({"material": material, "preview": lines})
    except Exception as e:
        print(f"Error previewing material: {str(e)}")
        return jsonify({"error": "Failed to preview material."}), 500


def delete_material():
    data = request.json
    folder = data.get("folder")
    filename = data.get("filename")

    # Sanitize inputs
    if not folder or not filename:
        return (
            jsonify({"success": False, "error": "Folder or filename not provided."}),
            400,
        )

    # Construct the file path consistently
    file_path = os.path.join(materials_directory, folder, filename)
    print(f"Attempting to delete: {file_path}")  # Debugging

    # Check if the file exists and delete it
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"File '{file_path}' deleted successfully.")
            return jsonify(
                {"success": True, "message": f"'{filename}' deleted successfully."}
            )
        except Exception as e:
            print(f"Error deleting file: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    else:
        print(f"File not found at: {file_path}")  # Debugging
        return jsonify({"success": False, "error": "File not found."}), 404


def upload_material():
    if not session.get("logged_in"):
        return jsonify({"error": "User not logged in"}), 403

    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Check file extension
    if not file.filename.endswith(".csv"):
        return jsonify({"error": "Please upload a .csv file"}), 400

    # Validate contents: Check if the file has three columns separated by commas
    content = file.read().decode("utf-8").strip()
    lines = content.split("\n")
    for line in lines:
        if len(line.split(",")) != 3:
            return (
                jsonify(
                    {
                        "error": "The CSV must have exactly three columns: wavelength, n, k"
                    }
                ),
                400,
            )

    # Save the file to the uploads directory specifically for user-uploaded files
    file_path = os.path.join(UPLOADS_DIRECTORY, file.filename)
    file.seek(0)  # Reset file pointer to the beginning after reading for validation
    file.save(file_path)
    print(f"File saved to: {file_path}")  # Debugging statement to verify file path

    return (
        jsonify({"message": "File uploaded successfully", "file_path": file_path}),
        200,
    )


def simulate_TRA(thicknesses, start_wavelength, end_wavelength):
    """
    Simulates TRA (Transmittance/Reflectance) for the given thicknesses and wavelength range.
    Args:
        thicknesses (list): List of layer thicknesses.
        start_wavelength (float): Start wavelength for the simulation.
        end_wavelength (float): End wavelength for the simulation.
    Returns:
        float: Average TRA value in the given range.
    """
    try:
        lam = np.linspace(start_wavelength, end_wavelength, 100)  # Wavelength range
        materials = session.get("materials", [])  # Retrieve materials from session
        theta = session.get("theta", 0)  # Angle of incidence
        incoh = session.get("incoh", 1000)  # Incoherence parameter

        stack = set_stack(materials, thicknesses, lam, theta, incoh)
        _, transmittance, _ = ATR1D(stack)

        # Compute the average transmittance over the wavelength range
        avg_transmittance = np.mean(transmittance["sp"])
        return avg_transmittance
    except Exception as e:
        print(f"Error in simulate_TRA: {str(e)}")
        raise e


def optimize():
    try:
        # Get data from the request
        data = request.json
        targets = data.get("targets", [])
        layers = data.get("layers", [])

        # Validate inputs
        if not targets or not layers:
            return (
                jsonify({"error": "Invalid payload. Missing targets or layers."}),
                400,
            )

        # Filter layers to exclude "Glass"
        layers_to_optimize = [
            layer for layer in layers if layer["material"].lower() != "glass"
        ]

        if not layers_to_optimize:
            return jsonify({"error": "No layers selected for optimization."}), 400

        # Get session parameters (e.g., start_wavelength, end_wavelength, etc.)
        start_wavelength = session.get("start_wavelength", 380)
        end_wavelength = session.get("end_wavelength", 1200)
        theta = session.get("theta", 0)
        incoh = session.get("incoh", 1000)

        # Extract current thicknesses for optimization
        initial_thicknesses = [layer["thickness"] for layer in layers_to_optimize]

        # Objective function for optimization
        def objective_function(thicknesses):
            # Update session layers with current thickness
            for i, layer in enumerate(layers_to_optimize):
                layer["thickness"] = thicknesses[i]

            # Simulate the current setup and calculate TRA
            try:
                avg_TRA = simulate_TRA(thicknesses, start_wavelength, end_wavelength)
                return (
                    -avg_TRA
                )  # Maximize TRA (negate because differential_evolution minimizes)
            except Exception as e:
                print(f"Simulation error: {str(e)}")
                return float("inf")  # Return high value for invalid configurations

        # Perform optimization using Differential Evolution
        bounds = [
            (1, 1000) for _ in initial_thicknesses
        ]  # Example bounds for thicknesses (1nm to 1000nm)
        result = differential_evolution(
            objective_function, bounds, strategy="best1bin", maxiter=1000, tol=0.01
        )

        if not result.success:
            print(f"Optimization failed: {result.message}")
            return jsonify({"error": "Optimization failed. Please try again."}), 500

        # Update layers with optimized thicknesses
        optimized_thicknesses = result.x.tolist()
        for i, layer in enumerate(layers_to_optimize):
            layer["thickness"] = optimized_thicknesses[i]

        return jsonify(
            {
                "success": True,
                "optimized_thicknesses": optimized_thicknesses,
                "objective_value": -result.fun,  # Negated back to reflect maximized TRA
            }
        )
    except Exception as e:
        print(f"Error during optimization: {str(e)}")
        return jsonify({"error": "Failed to optimize layers."}), 500


def save_targets():
    try:
        # Get targets from the request
        targets = request.json.get("targets", [])

        # Validate targets (ensure required fields are present)
        validated_targets = []
        for target in targets:
            if not all(
                k in target
                for k in [
                    "kind",
                    "reflTran",
                    "polarization",
                    "wavelengthBegin",
                    "wavelengthEnd",
                    "targetBegin",
                    "targetEnd",
                    "tolerance",
                    "environment",
                ]
            ):
                return jsonify({"error": "Invalid target format"}), 400
            validated_targets.append(target)

        # Save to session (or optionally to a database)
        session["targets"] = validated_targets

        return jsonify({"success": True, "targets_saved": len(validated_targets)})
    except Exception as e:
        print(f"Error saving targets: {str(e)}")
        return jsonify({"error": "Failed to save targets."}), 500


def calculate():
    try:
        data = request.json
        start_wavelength = float(data.get("start_wavelength", 380))
        end_wavelength = float(data.get("end_wavelength", 1200))
        lam = np.linspace(start_wavelength, end_wavelength, 851)
        theta = float(data.get("theta", 0))

        if theta is None:
            return jsonify({"error": "Theta value is missing"}), 400

        # Check for None values
        if start_wavelength is None or end_wavelength is None or theta is None:
            return jsonify({"error": "Missing input values"}), 400

        # Convert to float
        try:
            start_wavelength = float(start_wavelength)
            end_wavelength = float(end_wavelength)
            theta = float(theta)
        except ValueError:
            return jsonify({"error": "Invalid input values"}), 400

        # Process Bragg1 and Bragg2 file paths with a check to avoid double prefixing
        bragg1_files = [
            os.path.normpath(
                file
                if file.startswith(UPLOAD_FOLDER)
                else os.path.join(UPLOAD_FOLDER, file.replace(" - ", os.sep))
            )
            for file in data.get("bragg1", [])
        ]
        bragg2_files = [
            os.path.normpath(
                file
                if file.startswith(UPLOAD_FOLDER)
                else os.path.join(UPLOAD_FOLDER, file.replace(" - ", os.sep))
            )
            for file in data.get("bragg2", [])
        ]

        # Construct materials list, handling "air" and GLS_NEW.csv as special cases
        materials = ["air"] + bragg1_files + [GLS_FILE_PATH] + bragg2_files + ["air"]

        # Print constructed paths for debugging
        print("Constructed materials paths:", materials)  # Debug print to verify paths

        # Retrieve other parameters
        dBragg1 = data.get("dBragg1", [34.13])
        dBragg2 = data.get("dBragg2", [53.91])
        dgls = data.get("dgls", 320000)
        theta = data.get("theta", 0)
        incoh = data.get("incoh", 1000)

        # Combine thicknesses for stack
        dPSC = dBragg1 + [dgls] + dBragg2

        # Check file paths for all materials except "air"
        for material_path in materials:
            if material_path != "air" and not os.path.exists(material_path):
                print(f"Error: File not found - {material_path}")  # Debug statement
                return jsonify({"error": f"File not found: {material_path}"}), 400

        # Create the stack and run the ATR1D simulation
        stack = set_stack(materials, dPSC, lam, theta, incoh)
        A, T_PSC_AZO_EVA_PV, R = ATR1D(stack)

        # Process results
        transmittance = np.array(T_PSC_AZO_EVA_PV["sp"])
        reflectance = np.array(R["sp"])
        absorptance = 1 - transmittance - reflectance

        # Calculate electrical properties
        IV = get_electric(lam, transmittance)
        jsc = IV["jsc"]

        # Prepare response
        response = {
            "wavelengths": lam.tolist(),
            "transmittance": transmittance.tolist(),
            "reflectance": reflectance.tolist(),
            "absorptance": absorptance.tolist(),
            "jsc": jsc,
        }
        return jsonify(response)
    except Exception as e:
        print(f"Error during calculation: {str(e)}")  # Log exception for debugging
        return jsonify({"error": str(e)}), 500


@login_required
def public_designs():
    print("Accessing /public_designs route")  # Debugging print
    try:
        return render_template(
            "private/public_designs.html", first_name=session.get("first_name")
        )
    except Exception as e:
        print(f"Error rendering template: {e}")
        return "Error loading page", 500


def get_public_designs():
    if not session.get("logged_in"):
        return jsonify({"error": "User not logged in"}), 403

    try:
        # Fetch all public designs and include user_email explicitly
        public_designs = db["designs"].find(
            {"visibility": "public"},
            {
                "_id": 0,
                "name": 1,
                "user_email": 1,
                "design": 1,
            },  # Ensure user_email is included
        )

        # Log the fetched designs for debugging
        designs_list = []
        for design in public_designs:
            print("Fetched design from DB:", design)  # Debugging log
            designs_list.append(
                {
                    "name": design.get("name", "Unnamed Design"),
                    "user_email": design.get("user_email", "Unknown User"),
                    "details": design.get("design", {}),
                }
            )

        print("Formatted designs list:", designs_list)  # Debugging log
        return jsonify({"designs": designs_list}), 200
    except Exception as e:
        print(f"Error fetching public designs: {str(e)}")
        return jsonify({"error": "Failed to fetch public designs"}), 500


def save_design():
    if not session.get("logged_in"):
        return jsonify({"error": "User not logged in"}), 403

    user_email = session.get("email")
    design_data = request.json

    try:
        # Extract design data
        name = design_data.get("name", "Unnamed Design")
        visibility = design_data.get(
            "visibility", "private"
        )  # Default to private if not specified
        front_materials = design_data.get("frontMaterials", [])
        front_thicknesses = design_data.get("frontThicknesses", [])
        back_materials = design_data.get("backMaterials", [])
        back_thicknesses = design_data.get("backThicknesses", [])
        glass_thickness = design_data.get("glassThickness", 0)
        start_wavelength = design_data.get("startWavelength", 0)
        end_wavelength = design_data.get("endWavelength", 0)
        theta = design_data.get("theta", 0)
        incoh = design_data.get("incoh", 0)

        # Construct the design document
        design_document = {
            "user_email": user_email,
            "name": name,
            "visibility": visibility,
            "design": {
                "name": name,
                "visibility": visibility,
                "frontMaterials": front_materials,
                "frontThicknesses": front_thicknesses,
                "backMaterials": back_materials,
                "backThicknesses": back_thicknesses,
                "glassThickness": glass_thickness,
                "startWavelength": start_wavelength,
                "endWavelength": end_wavelength,
                "theta": theta,
                "incoh": incoh,
            },
        }

        # Insert the document into the database
        db["designs"].insert_one(design_document)

        return jsonify({"success": True}), 201
    except Exception as e:
        print(f"Error saving design: {str(e)}")
        return jsonify({"error": "Failed to save design."}), 500


def get_user_designs():
    if not session.get("logged_in"):
        return jsonify({"error": "User not logged in"}), 403

    user_email = session.get("email")
    if not user_email:
        return jsonify({"error": "User email not found in session"}), 403

    try:
        # Fetch designs for the logged-in user
        designs = db["designs"].find(
            {"user_email": user_email}, {"_id": 0, "design": 1}
        )
        design_list = []

        for design in designs:
            if "design" not in design:
                print(f"Missing 'design' key in document: {design}")
            else:
                design_list.append(
                    {
                        "name": design["design"].get("name", "Unnamed Design"),
                        "details": design["design"],
                    }
                )

        for design in design_list:
            design["details"]["theta"] = design["details"].get(
                "theta", 0
            )  # Default to 0 if missing

        return jsonify({"designs": design_list}), 200
    except Exception as e:
        print(f"Error retrieving designs: {str(e)}")
        return jsonify({"error": "Failed to retrieve designs"}), 500


def load_design():
    if not session.get("logged_in"):
        return jsonify({"error": "User not logged in"}), 403

    design_name = request.args.get("design_name")
    if not design_name:
        return jsonify({"error": "Design name is required"}), 400

    user_email = session.get("email")
    try:
        design = db["designs"].find_one(
            {"user_email": user_email, "design.name": design_name},
            {"_id": 0, "design": 1},
        )
        if not design:
            return jsonify({"error": "Design not found"}), 404

        return jsonify({"design": design["design"]}), 200
    except Exception as e:
        print(f"Error loading design: {str(e)}")
        return jsonify({"error": "Failed to load design"}), 500


def delete_design():
    if not session.get("logged_in"):
        return jsonify({"error": "User not logged in"}), 403

    user_email = session.get("email")
    if not user_email:
        return jsonify({"error": "User email not found in session"}), 403

    data = request.json  # Get JSON payload
    design_name = data.get("name")  # Extract design name

    print(f"Delete request received for user: {user_email}")  # Log user email
    print(f"Delete request received for design name: {design_name}")  # Log design name

    if not design_name:
        return jsonify({"error": "Design name is required"}), 400

    try:
        # Ensure the query matches the structure of your MongoDB document
        result = db["designs"].delete_one(
            {
                "user_email": user_email,  # Match by user email
                "design.name": design_name,  # Match by nested design name
            }
        )

        if result.deleted_count == 0:
            print("No design found to delete.")  # Debugging log
            return jsonify({"error": "Design not found"}), 404

        print(f"Deleted design successfully: {design_name}")  # Debugging log
        return jsonify({"success": True}), 200
    except Exception as e:
        print(f"Error deleting design: {str(e)}")  # Log exception
        return jsonify({"error": "Failed to delete design"}), 500


def get_layers():
    # Fetch the layers from the session
    layers = session.get("layers", [])
    return jsonify({"layers": layers})


def get_color_chart():
    try:
        data = request.json
        print("Received data:", data)  # Log the incoming data
        x = data.get("x", 0.0)
        y = data.get("y", 0.0)
        luminosity = data.get("luminosity", None)

        # Generate the color chart
        base64_image = plot_color_chart(x, y, luminosity)

        # Return the response
        response = jsonify(
            {
                "image": base64_image,
                "details": {
                    "x": x,
                    "y": y,
                    "luminosity": luminosity,
                    "dominantWavelength": "573 nm",
                },
            }
        )
        print("Returning response:", response.json)  # Log the response
        return response
    except Exception as e:
        print("Error in /get_color_chart:", str(e))
        return jsonify({"error": str(e)}), 500
